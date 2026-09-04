"""Persistent non-secret settings for the interactive console.

The INI file is intentionally limited to operational parameters. API keys,
tokens, passwords and other credentials remain environment/session-only and
are never written by this module.
"""
from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
import io
import os
from pathlib import Path
from typing import Any, Mapping

from searchgeo.provider_registry import get_provider_registration
from searchgeo.provider_runtime_policy import (
    AI_TIMEOUT_ENV,
    WEB_PERFORMANCE_TIMEOUT_ENV,
    provider_reasoning_env,
)

CONSOLE_INI_ENV = "SEARCHGEO_CONSOLE_INI"
DEFAULT_CONSOLE_INI = "searchgeo-console.ini"
CONFIG_VERSION = "1"


@dataclass(frozen=True, slots=True)
class ConfigLoadResult:
    path: Path
    created: bool
    warnings: tuple[str, ...] = ()


def resolve_config_path(
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> Path:
    environment = env if env is not None else os.environ
    configured = (environment.get(CONSOLE_INI_ENV) or "").strip()
    base = cwd if cwd is not None else Path.cwd()
    path = Path(configured).expanduser() if configured else base / DEFAULT_CONSOLE_INI
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _optional(value: Any) -> str:
    return "" if value is None else str(value)


def _state_values(state: Any) -> dict[str, dict[str, str]]:
    """Return only persistable, non-secret settings."""
    return {
        "console": {
            "config_version": CONFIG_VERSION,
            "input_mode": str(state.input_mode),
            "target": str(state.target),
            "project": str(state.project),
            "language": str(state.language),
            "market": str(state.market),
            "max_pages": str(int(state.max_pages)),
            "audits_root": str(state.audits_root),
            "device": str(state.device),
        },
        "ai": {
            "provider": str(state.ai_provider),
            "model": _optional(state.ai_model),
            "reasoning_effort": _optional(getattr(state, "ai_reasoning", None)),
            "timeout_seconds": f"{float(state.ai_timeout):g}",
            "content_remediation": _bool_text(bool(state.content_remediation)),
        },
        "web_performance": {
            "enabled": _bool_text(bool(state.web_performance)),
            "max_pages": str(int(state.web_max_pages)),
            "timeout_seconds": f"{float(state.web_timeout):g}",
            "field_source": str(state.field_source),
            "lighthouse_categories": str(state.lighthouse_categories),
        },
        "synthetic_apdex": {
            "enabled": _bool_text(bool(state.synthetic_apdex)),
            "threshold_seconds": _optional(state.apdex_threshold),
            "samples_per_context": str(int(state.apdex_samples)),
            "max_attempts_per_context": str(int(state.apdex_max_attempts)),
            "max_pages": str(int(state.apdex_max_pages)),
            "timeout_seconds": f"{float(state.apdex_timeout):g}",
            "delay_seconds": f"{float(state.apdex_delay):g}",
            "concurrency": str(int(state.apdex_concurrency)),
        },
    }


def configuration_fingerprint(state: Any) -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...]:
    values = _state_values(state)
    return tuple((section, tuple(sorted(items.items()))) for section, items in sorted(values.items()))


def _parser_for_state(state: Any) -> ConfigParser:
    parser = ConfigParser(interpolation=None)
    for section, values in _state_values(state).items():
        parser[section] = values
    return parser


def save_console_config(state: Any, path: Path | None = None) -> Path:
    destination = path or resolve_config_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    parser = _parser_for_state(state)
    stream = io.StringIO()
    stream.write("; SearchGEO interactive console settings\n")
    stream.write("; API keys, tokens, passwords and other secrets are intentionally NOT persisted.\n")
    stream.write("; Use environment variables or the console session to provide credentials.\n\n")
    parser.write(stream)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(stream.getvalue(), encoding="utf-8", newline="\n")
    os.replace(temporary, destination)
    if hasattr(state, "config_path"):
        state.config_path = str(destination)
    if hasattr(state, "config_dirty"):
        state.config_dirty = False
    return destination


def _parse_bool(value: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("use true/false")


def _assign(state: Any, section: str, option: str, raw: str) -> None:
    key = (section, option)
    if key == ("console", "input_mode"):
        value = raw.strip().casefold()
        if value not in {"url", "file"}: raise ValueError("use url ou file")
        state.input_mode = value
    elif key == ("console", "target"): state.target = raw.strip()
    elif key == ("console", "project"): state.project = raw.strip()
    elif key == ("console", "language"): state.language = raw.strip() or state.language
    elif key == ("console", "market"): state.market = raw.strip() or state.market
    elif key == ("console", "max_pages"):
        value = int(raw)
        if value <= 0: raise ValueError("use inteiro > 0")
        state.max_pages = value
    elif key == ("console", "audits_root"): state.audits_root = raw.strip() or state.audits_root
    elif key == ("console", "device"):
        value = raw.strip().casefold()
        if value not in {"mobile", "desktop", "both"}: raise ValueError("use mobile, desktop ou both")
        state.device, state.current_device = value, value.upper()
    elif key == ("ai", "provider"): state.ai_provider = raw.strip().casefold() or "none"
    elif key == ("ai", "model"): state.ai_model = raw.strip() or None
    elif key == ("ai", "reasoning_effort"): state.ai_reasoning = raw.strip().upper() or None
    elif key == ("ai", "timeout_seconds"):
        value = float(raw)
        if value <= 0: raise ValueError("use número > 0")
        state.ai_timeout = value
    elif key == ("ai", "content_remediation"): state.content_remediation = _parse_bool(raw)
    elif key == ("web_performance", "enabled"): state.web_performance = _parse_bool(raw)
    elif key == ("web_performance", "max_pages"):
        value = int(raw)
        if value < 0: raise ValueError("use inteiro >= 0")
        state.web_max_pages = value
    elif key == ("web_performance", "timeout_seconds"):
        value = float(raw)
        if value <= 0: raise ValueError("use número > 0")
        state.web_timeout = value
    elif key == ("web_performance", "field_source"):
        value = raw.strip().casefold()
        if value not in {"auto", "pagespeed", "crux", "none"}: raise ValueError("use auto, pagespeed, crux ou none")
        state.field_source = value
    elif key == ("web_performance", "lighthouse_categories"):
        state.lighthouse_categories = raw.strip() or state.lighthouse_categories
    elif key == ("synthetic_apdex", "enabled"): state.synthetic_apdex = _parse_bool(raw)
    elif key == ("synthetic_apdex", "threshold_seconds"):
        state.apdex_threshold = None if not raw.strip() else float(raw)
    elif key == ("synthetic_apdex", "samples_per_context"):
        value = int(raw)
        if value < 1: raise ValueError("use inteiro >= 1")
        state.apdex_samples = value
    elif key == ("synthetic_apdex", "max_attempts_per_context"):
        value = int(raw)
        if value < 1: raise ValueError("use inteiro >= 1")
        state.apdex_max_attempts = value
    elif key == ("synthetic_apdex", "max_pages"):
        value = int(raw)
        if value < 0: raise ValueError("use inteiro >= 0")
        state.apdex_max_pages = value
    elif key == ("synthetic_apdex", "timeout_seconds"):
        value = float(raw)
        if value <= 0: raise ValueError("use número > 0")
        state.apdex_timeout = value
    elif key == ("synthetic_apdex", "delay_seconds"):
        value = float(raw)
        if value < 0: raise ValueError("use número >= 0")
        state.apdex_delay = value
    elif key == ("synthetic_apdex", "concurrency"):
        value = int(raw)
        if value not in {1, 2}: raise ValueError("use 1 ou 2")
        state.apdex_concurrency = value


def load_console_config(state: Any, path: Path | None = None) -> ConfigLoadResult:
    source = path or resolve_config_path()
    if not source.exists():
        save_console_config(state, source)
        return ConfigLoadResult(source, True, ())
    parser = ConfigParser(interpolation=None)
    try:
        with source.open("r", encoding="utf-8") as stream:
            parser.read_file(stream)
    except (OSError, UnicodeError) as exc:
        return ConfigLoadResult(source, False, (f"não foi possível ler {source}: {type(exc).__name__}",))
    warnings: list[str] = []
    for section, values in _state_values(state).items():
        if not parser.has_section(section):
            continue
        for option in values:
            if option == "config_version" or not parser.has_option(section, option):
                continue
            raw = parser.get(section, option, raw=True)
            try:
                _assign(state, section, option, raw)
            except (ValueError, TypeError) as exc:
                warnings.append(f"{section}.{option}: {exc}")
    if hasattr(state, "config_path"):
        state.config_path = str(source)
    if hasattr(state, "config_dirty"):
        state.config_dirty = False
    return ConfigLoadResult(source, False, tuple(warnings))


def sync_nonsecret_runtime_environment(state: Any) -> None:
    """Project effective non-secret console settings into adapter environment."""
    os.environ[AI_TIMEOUT_ENV] = f"{float(state.ai_timeout):g}"
    os.environ[WEB_PERFORMANCE_TIMEOUT_ENV] = f"{float(state.web_timeout):g}"
    registration = get_provider_registration(str(state.ai_provider))
    if registration is not None and getattr(state, "ai_reasoning", None):
        variable = provider_reasoning_env(registration.provider_name)
        if variable:
            os.environ[variable] = str(state.ai_reasoning).upper()
