"""M3 execution glue: browser rendering and independent Desktop/Mobile snapshots."""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from searchgeo.domain import DeviceContext, PageSnapshot, new_id, utc_now
from searchgeo.m2 import M2ExecutionResult
from searchgeo.persistence import AuditPersistence, AuditWorkspace
from searchgeo.rendering import BrowserRenderResult, BrowserRenderer, RenderErrorKind


_RENDERING_MODE = "PLAYWRIGHT_CHROMIUM"
_DEVICES = (DeviceContext.DESKTOP, DeviceContext.MOBILE)


class Renderer(Protocol):
    def render(self, url: str, device: DeviceContext) -> BrowserRenderResult: ...


@dataclass(frozen=True, slots=True)
class RenderFailure:
    page_id: str
    device: DeviceContext
    error_kind: str


@dataclass(frozen=True, slots=True)
class M3ExecutionResult:
    snapshot_ids: dict[str, dict[DeviceContext, str]]
    failures: tuple[RenderFailure, ...]


def execute_m3(
    m2_result: M2ExecutionResult,
    persistence: AuditPersistence,
    workspace: AuditWorkspace,
    *,
    renderer: Renderer | None = None,
) -> M3ExecutionResult:
    """Render every M2 page independently for Desktop and Mobile and persist snapshots."""

    active_renderer: Renderer = renderer or BrowserRenderer()
    renderer_context = active_renderer if isinstance(active_renderer, BrowserRenderer) else nullcontext(active_renderer)
    snapshot_ids: dict[str, dict[DeviceContext, str]] = {}
    failures: list[RenderFailure] = []

    with renderer_context as session_renderer:
        for discovered in m2_result.discovery.pages:
            url = discovered.normalized_url
            page_id = m2_result.page_ids[url]
            page = persistence.pages.get(page_id)
            if page is None or page.normalized_url != url:
                raise ValueError(f"M2 page mapping is inconsistent for {url}")

            acquisition = m2_result.discovery.page_acquisitions[url]
            raw_artifact_ref = m2_result.raw_artifact_refs.get(url)
            if acquisition.body and not raw_artifact_ref:
                raise ValueError(f"M2 RAW artifact reference is missing for {url}")
            if raw_artifact_ref and not (workspace.root / raw_artifact_ref).is_file():
                raise FileNotFoundError(f"M2 RAW artifact is not re-openable: {raw_artifact_ref}")

            per_device: dict[DeviceContext, str] = {}
            for device in _DEVICES:
                try:
                    render_result = session_renderer.render(url, device)
                except Exception:
                    render_result = _unexpected_failure(url, device)

                snapshot_id = new_id("SNP")
                rendered_artifact_ref = _write_rendered_artifact(
                    workspace,
                    page_id,
                    device,
                    snapshot_id,
                    render_result.rendered_html,
                )
                browser_metadata = dict(render_result.browser_metadata)
                browser_metadata["raw_http"] = {
                    "requested_url": acquisition.requested_url,
                    "final_url": acquisition.final_url,
                    "status": acquisition.status,
                    "redirect_count": len(acquisition.redirects),
                    "network_error": acquisition.network_error.kind.value if acquisition.network_error else None,
                }
                browser_metadata["render_succeeded"] = render_result.succeeded

                snapshot = PageSnapshot(
                    snapshot_id=snapshot_id,
                    page_id=page_id,
                    device=device,
                    requested_url=url,
                    final_url=render_result.final_url or acquisition.final_url,
                    captured_at=utc_now(),
                    http_status=(
                        render_result.http_status
                        if render_result.http_status is not None
                        else acquisition.status
                    ),
                    content_type=(
                        render_result.content_type
                        or acquisition.header("Content-Type")
                    ),
                    rendering_mode=_RENDERING_MODE,
                    raw_artifact_ref=raw_artifact_ref,
                    rendered_artifact_ref=rendered_artifact_ref,
                    browser_metadata=browser_metadata,
                )
                persistence.snapshots.add(snapshot)
                per_device[device] = snapshot.snapshot_id

                if render_result.error_kind is not None:
                    failures.append(
                        RenderFailure(
                            page_id=page_id,
                            device=device,
                            error_kind=render_result.error_kind.value,
                        )
                    )
            snapshot_ids[page_id] = per_device

    return M3ExecutionResult(snapshot_ids=snapshot_ids, failures=tuple(failures))


def _write_rendered_artifact(
    workspace: AuditWorkspace,
    page_id: str,
    device: DeviceContext,
    snapshot_id: str,
    rendered_html: str | None,
) -> str | None:
    if rendered_html is None:
        return None
    directory = workspace.artifacts / "rendered" / page_id / device.value.lower()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{snapshot_id}.html"
    path.write_text(rendered_html, encoding="utf-8", newline="\n")
    return Path("artifacts", "rendered", page_id, device.value.lower(), path.name).as_posix()


def _unexpected_failure(url: str, device: DeviceContext) -> BrowserRenderResult:
    return BrowserRenderResult(
        requested_url=url,
        final_url=None,
        http_status=None,
        content_type=None,
        rendered_html=None,
        browser_metadata={
            "engine": "renderer-adapter",
            "profile": {"device": device.value},
            "render_error": RenderErrorKind.RENDERER_ERROR.value,
        },
        error_kind=RenderErrorKind.RENDERER_ERROR,
    )
