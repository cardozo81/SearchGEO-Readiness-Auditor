"""CLI/environment configuration contract for M23 Synthetic Navigation Apdex."""
from __future__ import annotations

import argparse
import math
import os
from typing import Any

from searchgeo.m23_apdex import SyntheticApdexConfig

APDEX_ENABLED_ENV = "SEARCHGEO_SYNTHETIC_APDEX"
APDEX_THRESHOLD_ENV = "SEARCHGEO_APDEX_THRESHOLD_SECONDS"
APDEX_RUNS_ENV = "SEARCHGEO_APDEX_RUNS_PER_CONTEXT"
APDEX_MAX_PAGES_ENV = "SEARCHGEO_APDEX_MAX_PAGES"
APDEX_TIMEOUT_ENV = "SEARCHGEO_APDEX_TIMEOUT_SECONDS"

DEFAULT_APDEX_RUNS_PER_CONTEXT = 10
DEFAULT_APDEX_MAX_PAGES = 1
DEFAULT_APDEX_TIMEOUT_SECONDS = 45.0


def register_apdex_arguments(audit_parser: argparse.ArgumentParser) -> None:
    """Add M23 options without changing any existing option semantics."""
    audit_parser.add_argument(
        "--synthetic-apdex",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "enable M23 Synthetic Navigation Apdex; default OFF or "
            f"{APDEX_ENABLED_ENV}; requires an explicit T"
        ),
    )
    audit_parser.add_argument(
        "--apdex-threshold-seconds",
        type=float,
        default=None,
        help=(
            "Apdex target threshold T in seconds; mandatory when M23 is enabled; "
            f"or {APDEX_THRESHOLD_ENV}"
        ),
    )
    audit_parser.add_argument(
        "--apdex-runs-per-context",
        type=int,
        default=None,
        help=(
            "repeated cold-context navigation samples per page/device; "
            f"default {DEFAULT_APDEX_RUNS_PER_CONTEXT} or {APDEX_RUNS_ENV}; "
            "1-99 samples are reported as a small group (*)"
        ),
    )
    audit_parser.add_argument(
        "--apdex-max-pages",
        type=int,
        default=None,
        help=(
            "maximum audited pages measured by Synthetic Apdex; 0 means all; "
            f"default {DEFAULT_APDEX_MAX_PAGES} or {APDEX_MAX_PAGES_ENV}"
        ),
    )
    audit_parser.add_argument(
        "--apdex-timeout-seconds",
        type=float,
        default=None,
        help=(
            "navigation timeout for each synthetic sample; must be > 4*T. "
            "When omitted it is max(45s, 4*T+5s), or use "
            f"{APDEX_TIMEOUT_ENV}"
        ),
    )


def configured_apdex(args: Any, env: dict[str, str] | os._Environ[str] | None = None) -> SyntheticApdexConfig:
    """Resolve M23 config with CLI > environment > safe defaults.

    Inactive tuning variables are deliberately ignored when M23 is OFF so an
    unrelated stale/malformed value cannot break the existing audit command.
    """
    environment = env if env is not None else os.environ
    enabled = _configured_bool(getattr(args, "synthetic_apdex", None), APDEX_ENABLED_ENV, False, environment)
    if not enabled:
        return SyntheticApdexConfig(enabled=False).validate()

    threshold = _optional_positive_float(
        getattr(args, "apdex_threshold_seconds", None),
        APDEX_THRESHOLD_ENV,
        environment,
    )
    if threshold is None:
        raise ValueError(
            "Synthetic Apdex requires explicit T: use --apdex-threshold-seconds "
            f"or {APDEX_THRESHOLD_ENV}"
        )
    runs = _positive_int(
        getattr(args, "apdex_runs_per_context", None),
        APDEX_RUNS_ENV,
        DEFAULT_APDEX_RUNS_PER_CONTEXT,
        environment,
    )
    max_pages = _nonnegative_int(
        getattr(args, "apdex_max_pages", None),
        APDEX_MAX_PAGES_ENV,
        DEFAULT_APDEX_MAX_PAGES,
        environment,
    )
    timeout = _optional_positive_float(
        getattr(args, "apdex_timeout_seconds", None),
        APDEX_TIMEOUT_ENV,
        environment,
    )
    if timeout is None:
        timeout = max(DEFAULT_APDEX_TIMEOUT_SECONDS, 4.0 * threshold + 5.0)

    return SyntheticApdexConfig(
        enabled=True,
        threshold_seconds=threshold,
        runs_per_context=runs,
        max_pages=max_pages,
        timeout_seconds=timeout,
    ).validate()


def _configured_bool(
    cli_value: bool | None,
    env_name: str,
    default: bool,
    env: dict[str, str] | os._Environ[str],
) -> bool:
    if cli_value is not None:
        return bool(cli_value)
    raw = (env.get(env_name) or "").strip()
    if not raw:
        return default
    value = raw.casefold()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{env_name} must be one of: true/false, 1/0, yes/no, on/off")


def _optional_positive_float(
    cli_value: float | None,
    env_name: str,
    env: dict[str, str] | os._Environ[str],
) -> float | None:
    if cli_value is not None:
        value = float(cli_value)
    else:
        raw = (env.get(env_name) or "").strip()
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{env_name} must be a positive number") from exc
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{env_name} / CLI value must be a positive finite number")
    return value


def _positive_int(
    cli_value: int | None,
    env_name: str,
    default: int,
    env: dict[str, str] | os._Environ[str],
) -> int:
    if cli_value is not None:
        value = int(cli_value)
    else:
        raw = (env.get(env_name) or "").strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{env_name} must be an integer >= 1") from exc
    if value < 1:
        raise ValueError(f"{env_name} / CLI value must be >= 1")
    return value


def _nonnegative_int(
    cli_value: int | None,
    env_name: str,
    default: int,
    env: dict[str, str] | os._Environ[str],
) -> int:
    if cli_value is not None:
        value = int(cli_value)
    else:
        raw = (env.get(env_name) or "").strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{env_name} must be an integer >= 0") from exc
    if value < 0:
        raise ValueError(f"{env_name} / CLI value must be >= 0")
    return value
