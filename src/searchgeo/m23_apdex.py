"""M23 controlled Synthetic Navigation Apdex measurement.

Apdex is calculated from repeated task timings under an explicit T. It is never
inferred from Lighthouse scores, Core Web Vitals, or PageSpeed request latency.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import math
import os
import platform
import sqlite3
import statistics
import sys
import time
from typing import Any, Protocol

from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError, sync_playwright

from searchgeo.domain import DeviceContext, new_id
from searchgeo.m23_persistence import M23Persistence, SyntheticApdexRun, SyntheticApdexSample, SyntheticApdexSummary
from searchgeo.operational_log import try_append_operational_event
from searchgeo.persistence import AuditWorkspace
from searchgeo.rendering import DESKTOP_PROFILE, MOBILE_PROFILE, BrowserProfile

TASK_NAVIGATION_LOAD = "NAVIGATION_LOAD"
SMALL_GROUP_THRESHOLD = 100
PROFILE_VERSION = "M23-PROFILE-001"


@dataclass(frozen=True, slots=True)
class SyntheticProfile:
    profile_id: str
    device: DeviceContext
    browser_profile: BrowserProfile
    cpu_slowdown: float
    rtt_ms: float
    download_kbps: float
    upload_kbps: float
    connection_type: str

    def validate(self) -> "SyntheticProfile":
        for name, value, minimum in (
            ("cpu_slowdown", self.cpu_slowdown, 1.0),
            ("rtt_ms", self.rtt_ms, 0.0),
            ("download_kbps", self.download_kbps, 0.000001),
            ("upload_kbps", self.upload_kbps, 0.000001),
        ):
            if not math.isfinite(value) or value < minimum:
                raise ValueError(f"{name} must be finite and >= {minimum:g}")
        return self

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "profile_version": PROFILE_VERSION,
            "device": self.device.value,
            "viewport": {
                "width": self.browser_profile.viewport_width,
                "height": self.browser_profile.viewport_height,
            },
            "user_agent": self.browser_profile.user_agent,
            "device_scale_factor": self.browser_profile.device_scale_factor,
            "is_mobile": self.browser_profile.is_mobile,
            "has_touch": self.browser_profile.has_touch,
            "cpu_slowdown": self.cpu_slowdown,
            "rtt_ms": self.rtt_ms,
            "download_kbps": self.download_kbps,
            "upload_kbps": self.upload_kbps,
            "connection_type": self.connection_type,
            "cache_policy": "COLD_CONTEXT",
        }


MOBILE_STANDARD_PROFILE = SyntheticProfile(
    profile_id="SEARCHGEO_MOBILE_SLOW4G_V1",
    device=DeviceContext.MOBILE,
    browser_profile=MOBILE_PROFILE,
    cpu_slowdown=4.0,
    rtt_ms=150.0,
    download_kbps=1638.4,
    upload_kbps=750.0,
    connection_type="cellular4g",
)

DESKTOP_STANDARD_PROFILE = SyntheticProfile(
    profile_id="SEARCHGEO_DESKTOP_DENSE4G_V1",
    device=DeviceContext.DESKTOP,
    browser_profile=DESKTOP_PROFILE,
    cpu_slowdown=1.0,
    rtt_ms=40.0,
    download_kbps=10240.0,
    upload_kbps=10240.0,
    connection_type="ethernet",
)


@dataclass(frozen=True, slots=True)
class SyntheticApdexConfig:
    enabled: bool = False
    threshold_seconds: float | None = None
    runs_per_context: int = 10
    max_pages: int = 1
    timeout_seconds: float = 45.0
    mobile_profile: SyntheticProfile = MOBILE_STANDARD_PROFILE
    desktop_profile: SyntheticProfile = DESKTOP_STANDARD_PROFILE

    def validate(self) -> "SyntheticApdexConfig":
        if not self.enabled:
            return replace(self, threshold_seconds=None)
        if self.threshold_seconds is None or not math.isfinite(self.threshold_seconds) or self.threshold_seconds <= 0:
            raise ValueError("Synthetic Apdex requires an explicit positive --apdex-threshold-seconds T")
        _validate_threshold_resolution(self.threshold_seconds)
        if self.runs_per_context < 1:
            raise ValueError("Apdex runs_per_context must be >= 1")
        if self.max_pages < 0:
            raise ValueError("Apdex max_pages must be >= 0 (0 means all audited pages)")
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 4.0 * self.threshold_seconds:
            raise ValueError("Apdex timeout_seconds must be greater than 4*T so tool timeout cannot precede the Frustrated boundary")
        self.mobile_profile.validate()
        self.desktop_profile.validate()
        return self


@dataclass(frozen=True, slots=True)
class NavigationMeasurement:
    status: str
    duration_ms: int | None
    http_status: int | None
    final_url: str | None
    error_code: str | None
    error_message: str | None
    profile_applied: bool
    cpu_method: str | None
    network_method: str | None


class SyntheticNavigationGateway(Protocol):
    def measure(self, *, url: str, profile: SyntheticProfile, timeout_seconds: float) -> NavigationMeasurement: ...
    def environment(self) -> dict[str, Any]: ...
    def close(self) -> None: ...


class PlaywrightSyntheticNavigationGateway:
    """Chromium measurement gateway with a fresh browser context for every sample."""

    def __init__(self, executable_path: str | None = None) -> None:
        self.executable_path = executable_path or os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        self._playwright = None
        self._browser = None
        self._startup_error: str | None = None

    def _start(self) -> None:
        if self._browser is not None or self._startup_error is not None:
            return
        try:
            self._playwright = sync_playwright().start()
            options: dict[str, Any] = {"headless": True}
            if self.executable_path:
                options["executable_path"] = self.executable_path
            self._browser = self._playwright.chromium.launch(**options)
        except Exception as exc:
            self._startup_error = type(exc).__name__
            self.close()

    def close(self) -> None:
        browser, playwright = self._browser, self._playwright
        self._browser = None
        self._playwright = None
        if browser is not None:
            try:
                browser.close()
            except PlaywrightError:
                pass
        if playwright is not None:
            try:
                playwright.stop()
            except Exception:
                pass

    def environment(self) -> dict[str, Any]:
        self._start()
        playwright_version = None
        try:
            from importlib.metadata import version
            playwright_version = version("playwright")
        except Exception:
            pass
        return {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor() or None,
            "logical_cpu_count": os.cpu_count(),
            "python_version": sys.version.split()[0],
            "playwright_version": playwright_version,
            "chromium_version": getattr(self._browser, "version", None) if self._browser is not None else None,
            "startup_error": self._startup_error,
        }

    def measure(self, *, url: str, profile: SyntheticProfile, timeout_seconds: float) -> NavigationMeasurement:
        self._start()
        if self._browser is None:
            return NavigationMeasurement(
                status="BROWSER_UNAVAILABLE", duration_ms=None, http_status=None, final_url=None,
                error_code=self._startup_error or "BROWSER_UNAVAILABLE", error_message=None,
                profile_applied=False, cpu_method=None, network_method=None,
            )
        context = page = session = None
        cpu_method = network_method = None
        try:
            context = self._browser.new_context(**profile.browser_profile.context_options)
            page = context.new_page()
            session = context.new_cdp_session(page)
            session.send("Network.enable")
            session.send("Network.setCacheDisabled", {"cacheDisabled": True})
            try:
                session.send("Emulation.setCPUThrottlingRate", {"rate": profile.cpu_slowdown})
                cpu_method = "CDP:Emulation.setCPUThrottlingRate"
            except PlaywrightError as exc:
                return _invalid_profile("CPU_PROFILE_ERROR", exc, cpu_method, network_method)

            network_method = _apply_network_profile(session, profile)
            started = time.monotonic()
            try:
                response = page.goto(url, wait_until="load", timeout=int(timeout_seconds * 1000.0))
                duration_ms = int((time.monotonic() - started) * 1000.0)
                http_status = response.status if response is not None else None
                status = "APPLICATION_ERROR" if http_status is not None and http_status >= 400 else "SUCCESS"
                return NavigationMeasurement(
                    status=status, duration_ms=duration_ms, http_status=http_status,
                    final_url=page.url, error_code=None, error_message=None,
                    profile_applied=True, cpu_method=cpu_method, network_method=network_method,
                )
            except PlaywrightTimeoutError:
                duration_ms = int((time.monotonic() - started) * 1000.0)
                return NavigationMeasurement(
                    status="TIMEOUT", duration_ms=duration_ms, http_status=None,
                    final_url=page.url if page is not None else None,
                    error_code="NAVIGATION_TIMEOUT", error_message="navigation exceeded configured timeout",
                    profile_applied=True, cpu_method=cpu_method, network_method=network_method,
                )
            except PlaywrightError as exc:
                duration_ms = int((time.monotonic() - started) * 1000.0)
                return NavigationMeasurement(
                    status="NAVIGATION_ERROR", duration_ms=duration_ms, http_status=None,
                    final_url=page.url if page is not None else None,
                    error_code=type(exc).__name__.upper(), error_message=_bounded(str(exc), 256),
                    profile_applied=True, cpu_method=cpu_method, network_method=network_method,
                )
        except PlaywrightError as exc:
            return _invalid_profile("PROFILE_SETUP_ERROR", exc, cpu_method, network_method)
        except Exception as exc:
            return _invalid_profile("MEASUREMENT_SETUP_ERROR", exc, cpu_method, network_method)
        finally:
            if session is not None:
                try:
                    session.detach()
                except PlaywrightError:
                    pass
            if page is not None:
                try:
                    page.close()
                except PlaywrightError:
                    pass
            if context is not None:
                try:
                    context.close()
                except PlaywrightError:
                    pass


def _invalid_profile(code: str, exc: Exception, cpu_method: str | None, network_method: str | None) -> NavigationMeasurement:
    return NavigationMeasurement(
        status="INVALID_SAMPLE", duration_ms=None, http_status=None, final_url=None,
        error_code=code, error_message=_bounded(str(exc), 256), profile_applied=False,
        cpu_method=cpu_method, network_method=network_method,
    )


def _apply_network_profile(session: Any, profile: SyntheticProfile) -> str:
    download_bps = profile.download_kbps * 1024.0 / 8.0
    upload_bps = profile.upload_kbps * 1024.0 / 8.0
    # New CDP split API is preferred. Chromium versions without it fall back to
    # the legacy command; the method is persisted so the report never hides it.
    try:
        conditions = {
            "offline": False,
            "latency": profile.rtt_ms,
            "downloadThroughput": download_bps,
            "uploadThroughput": upload_bps,
            "connectionType": profile.connection_type,
        }
        session.send("Network.overrideNetworkState", conditions)
        session.send(
            "Network.emulateNetworkConditionsByRule",
            {
                "offline": False,
                "matchedNetworkConditions": [{
                    "urlPattern": "*",
                    "latency": profile.rtt_ms,
                    "downloadThroughput": download_bps,
                    "uploadThroughput": upload_bps,
                }],
            },
        )
        return "CDP:overrideNetworkState+emulateNetworkConditionsByRule"
    except PlaywrightError:
        session.send(
            "Network.emulateNetworkConditions",
            {
                "offline": False,
                "latency": profile.rtt_ms,
                "downloadThroughput": download_bps,
                "uploadThroughput": upload_bps,
                "connectionType": profile.connection_type,
            },
        )
        return "CDP:Network.emulateNetworkConditions(legacy-fallback)"


@dataclass(frozen=True, slots=True)
class M23ExecutionResult:
    enabled: bool
    status: str
    pages_considered: int
    contexts_considered: int
    attempted_samples: int
    valid_samples: int
    invalid_samples: int
    small_group_summaries: int


def execute_m23_apdex(
    *,
    audit_id: str,
    workspace: AuditWorkspace,
    config: SyntheticApdexConfig | None = None,
    gateway: SyntheticNavigationGateway | None = None,
) -> M23ExecutionResult:
    cfg = (config or SyntheticApdexConfig()).validate()
    owned_gateway = gateway is None
    runner = gateway or PlaywrightSyntheticNavigationGateway()
    now = _utc_now()
    try_append_operational_event(
        workspace, "M23_STARTED", audit_id=audit_id, enabled=cfg.enabled,
        task_id=TASK_NAVIGATION_LOAD, threshold_seconds=cfg.threshold_seconds,
        runs_per_context=cfg.runs_per_context, max_pages=cfg.max_pages,
        timeout_seconds=cfg.timeout_seconds,
    )
    host = runner.environment()
    configuration = {
        "task_id": TASK_NAVIGATION_LOAD,
        "task_start": "immediately before page.goto",
        "task_end": "page.goto wait_until=load completed",
        "cache_policy": "COLD_CONTEXT",
        "small_group_threshold": SMALL_GROUP_THRESHOLD,
        "mobile_profile": cfg.mobile_profile.as_dict(),
        "desktop_profile": cfg.desktop_profile.as_dict(),
    }
    if not cfg.enabled:
        with M23Persistence(workspace) as store:
            store.upsert_run(SyntheticApdexRun(
                audit_id=audit_id, enabled=False, status="DISABLED", task_id=TASK_NAVIGATION_LOAD,
                threshold_seconds=None, frustration_seconds=None, runs_per_context=cfg.runs_per_context,
                page_limit=cfg.max_pages, pages_considered=0, contexts_considered=0,
                attempted_samples=0, valid_samples=0, invalid_samples=0,
                configuration=configuration, host_environment=host,
                reason="SYNTHETIC_APDEX_DISABLED", updated_at=now,
            ))
        if owned_gateway:
            runner.close()
        return M23ExecutionResult(False, "DISABLED", 0, 0, 0, 0, 0, 0)

    threshold = float(cfg.threshold_seconds)
    contexts = _audit_contexts(workspace, audit_id)
    ordered_pages: list[str] = []
    for row in contexts:
        if row["page_id"] not in ordered_pages:
            ordered_pages.append(str(row["page_id"]))
    selected = set(ordered_pages if cfg.max_pages == 0 else ordered_pages[: cfg.max_pages])
    contexts = [row for row in contexts if row["page_id"] in selected]
    attempted = valid = invalid = small = 0

    try:
        with M23Persistence(workspace) as store:
            for row in contexts:
                device = DeviceContext(str(row["device"]))
                profile = cfg.mobile_profile if device is DeviceContext.MOBILE else cfg.desktop_profile
                url = str(row["final_url"] or row["normalized_url"])
                samples: list[tuple[str, int]] = []
                invalid_for_context = 0
                for run_index in range(1, cfg.runs_per_context + 1):
                    attempted += 1
                    measurement = runner.measure(url=url, profile=profile, timeout_seconds=cfg.timeout_seconds)
                    classification = _classification(measurement, threshold)
                    if classification is None:
                        invalid += 1
                        invalid_for_context += 1
                    else:
                        valid += 1
                        samples.append((classification, int(measurement.duration_ms or 0)))
                    store.add_sample(SyntheticApdexSample(
                        sample_id=new_id("APX"), audit_id=audit_id, page_id=str(row["page_id"]),
                        snapshot_id=str(row["snapshot_id"]), device=device.value, url=url,
                        run_index=run_index, task_id=TASK_NAVIGATION_LOAD,
                        profile_id=profile.profile_id, profile_version=PROFILE_VERSION,
                        status=measurement.status, classification=classification,
                        duration_ms=measurement.duration_ms, http_status=measurement.http_status,
                        final_url=measurement.final_url, error_code=measurement.error_code,
                        error_message=_bounded(measurement.error_message, 256),
                        cpu_method=measurement.cpu_method, network_method=measurement.network_method,
                        cache_policy="COLD_CONTEXT", captured_at=_utc_now(),
                    ))
                    try_append_operational_event(
                        workspace, "M23_APDEX_SAMPLE",
                        level="WARNING" if classification in {"FRUSTRATED", None} else "INFO",
                        audit_id=audit_id, device=device.value, url=url, run_index=run_index,
                        profile_id=profile.profile_id, status=measurement.status,
                        classification=classification, duration_ms=measurement.duration_ms,
                        http_status=measurement.http_status, error_code=measurement.error_code,
                        cpu_method=measurement.cpu_method, network_method=measurement.network_method,
                    )
                summary = _summary(
                    audit_id=audit_id, page_id=str(row["page_id"]), device=device.value,
                    url=url, profile=profile, threshold=threshold, samples=samples,
                    invalid_samples=invalid_for_context,
                )
                if summary.small_group and summary.valid_samples:
                    small += 1
                store.upsert_summary(summary)

            if not contexts:
                status, reason = "NO_CONTEXTS", "NO_RENDERED_CONTEXTS"
            elif valid == 0:
                status, reason = "UNAVAILABLE", "NO_VALID_SYNTHETIC_SAMPLES"
            elif invalid:
                status, reason = "PARTIAL", "ONE_OR_MORE_SYNTHETIC_SAMPLES_INVALID"
            else:
                status, reason = "SUCCESS", None
            store.upsert_run(SyntheticApdexRun(
                audit_id=audit_id, enabled=True, status=status, task_id=TASK_NAVIGATION_LOAD,
                threshold_seconds=threshold, frustration_seconds=4.0 * threshold,
                runs_per_context=cfg.runs_per_context, page_limit=cfg.max_pages,
                pages_considered=len(selected), contexts_considered=len(contexts),
                attempted_samples=attempted, valid_samples=valid, invalid_samples=invalid,
                configuration=configuration, host_environment=host, reason=reason,
                updated_at=_utc_now(),
            ))
    finally:
        if owned_gateway:
            runner.close()

    try_append_operational_event(
        workspace, "M23_APDEX_COMPLETED", audit_id=audit_id, status=status,
        pages_considered=len(selected), contexts_considered=len(contexts),
        attempted_samples=attempted, valid_samples=valid, invalid_samples=invalid,
        small_group_summaries=small,
    )
    return M23ExecutionResult(True, status, len(selected), len(contexts), attempted, valid, invalid, small)


def _classification(item: NavigationMeasurement, threshold_seconds: float) -> str | None:
    if not item.profile_applied or item.duration_ms is None:
        return None
    if item.status in {"APPLICATION_ERROR", "TIMEOUT", "NAVIGATION_ERROR"}:
        return "FRUSTRATED"
    seconds = item.duration_ms / 1000.0
    if seconds <= threshold_seconds:
        return "SATISFIED"
    if seconds <= 4.0 * threshold_seconds:
        return "TOLERATING"
    return "FRUSTRATED"


def _summary(*, audit_id: str, page_id: str, device: str, url: str, profile: SyntheticProfile, threshold: float, samples: list[tuple[str, int]], invalid_samples: int) -> SyntheticApdexSummary:
    counts = {name: sum(1 for classification, _ in samples if classification == name) for name in ("SATISFIED", "TOLERATING", "FRUSTRATED")}
    durations = sorted(duration for _, duration in samples)
    total = len(samples)
    score = (counts["SATISFIED"] + 0.5 * counts["TOLERATING"]) / total if total else None
    return SyntheticApdexSummary(
        summary_id=new_id("APS"), audit_id=audit_id, page_id=page_id, device=device,
        url=url, task_id=TASK_NAVIGATION_LOAD, profile_id=profile.profile_id,
        threshold_seconds=threshold, frustration_seconds=4.0 * threshold,
        valid_samples=total, invalid_samples=invalid_samples,
        satisfied_count=counts["SATISFIED"], tolerating_count=counts["TOLERATING"],
        frustrated_count=counts["FRUSTRATED"], apdex_score=round(score, 6) if score is not None else None,
        small_group=0 < total < SMALL_GROUP_THRESHOLD,
        median_ms=statistics.median(durations) if durations else None,
        p75_ms=_percentile(durations, 0.75), p95_ms=_percentile(durations, 0.95),
        calculated_at=_utc_now(),
    )


def _percentile(values: list[int], fraction: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return float(values[0])
    position = (len(values) - 1) * fraction
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return float(values[low])
    weight = position - low
    return float(values[low] * (1.0 - weight) + values[high] * weight)


def _audit_contexts(workspace: AuditWorkspace, audit_id: str) -> list[dict[str, Any]]:
    connection = sqlite3.connect(workspace.database)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT p.page_id,p.normalized_url,s.snapshot_id,s.device,s.final_url
            FROM pages p JOIN page_snapshots s ON s.page_id=p.page_id
            WHERE p.audit_id=?
            ORDER BY p.normalized_url,p.page_id,s.device,s.snapshot_id
            """,
            (audit_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def _validate_threshold_resolution(value: float) -> None:
    tolerance = 1e-9
    if value < 10:
        scaled = value * 10.0
        valid = abs(scaled - round(scaled)) <= tolerance
        hint = "0.1 second"
    elif value < 100:
        valid = abs(value - round(value)) <= tolerance
        hint = "1 second"
    elif value < 1000:
        scaled = value / 10.0
        valid = abs(scaled - round(scaled)) <= tolerance
        hint = "10 seconds"
    else:
        exponent = math.floor(math.log10(value)) - 1
        step = 10 ** exponent
        scaled = value / step
        valid = abs(scaled - round(scaled)) <= tolerance
        hint = "two significant digits"
    if not valid:
        raise ValueError(f"Apdex threshold T does not follow specification resolution; use {hint} precision for this range")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bounded(value: str | None, limit: int) -> str | None:
    if value is None:
        return None
    return value[:limit]
