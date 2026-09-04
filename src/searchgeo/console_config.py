"""Configuration and preflight rules for the optional interactive console."""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import sys
from typing import Mapping

from searchgeo.cli import validate_target
from searchgeo.provider_registry import (
    auto_provider_ids,
    get_provider_registration,
    provider_environment_names,
    provider_registrations,
)
from searchgeo.provider_runtime_policy import (
    AI_TIMEOUT_ENV,
    DEFAULT_AI_TIMEOUT_SECONDS,
    DEFAULT_WEB_PERFORMANCE_TIMEOUT_SECONDS,
    EXTENSION_REASONING_ENV,
    LOWEST_REASONING,
    REASONING_OPTIONS,
    SIMPLE_DEFAULT_MODELS,
    WEB_PERFORMANCE_TIMEOUT_ENV,
    configured_reasoning,
    provider_reasoning_env,
)
from searchgeo.url_utils import normalize_url, normalized_origin


_REGISTRATIONS = provider_registrations()
PROVIDERS = {item.id: item.provider_name for item in _REGISTRATIONS}
KEY_ENV = {item.provider_name: item.key_env for item in _REGISTRATIONS}
MODEL_ENV = {item.provider_name: item.model_env for item in _REGISTRATIONS}
DEFAULT_MODELS = dict(SIMPLE_DEFAULT_MODELS)
SUPPORTED_MODELS = {item.provider_name: item.supported_models for item in _REGISTRATIONS}
REASONING_ENV = {
    item.provider_name: provider_reasoning_env(item.provider_name)
    for item in _REGISTRATIONS
    if provider_reasoning_env(item.provider_name)
}
PROVIDER_MENU_CHOICES = ("none", *(item.id for item in _REGISTRATIONS), "auto")

_BASE_ENV_NAMES = (
    "SEARCHGEO_CONFIG",
    "SEARCHGEO_LOG_LEVEL",
    "SEARCHGEO_DEVICE_CONTEXT",
    AI_TIMEOUT_ENV,
    "SEARCHGEO_AI_CONTENT_REMEDIATION",
    "SEARCHGEO_WEB_PERFORMANCE",
    "SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES",
    WEB_PERFORMANCE_TIMEOUT_ENV,
    "SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE",
    "SEARCHGEO_LIGHTHOUSE_CATEGORIES",
    "SEARCHGEO_PAGESPEED_API_KEY",
    "SEARCHGEO_CRUX_API_KEY",
    *EXTENSION_REASONING_ENV.values(),
    "PLAYWRIGHT_CHROMIUM_EXECUTABLE",
)
ENV_NAMES = tuple(dict.fromkeys((*_BASE_ENV_NAMES, *provider_environment_names())))
SECRET_NAMES = frozenset(
    {
        *(item.key_env for item in _REGISTRATIONS),
        "SEARCHGEO_PAGESPEED_API_KEY",
        "SEARCHGEO_CRUX_API_KEY",
    }
)


@dataclass(frozen=True, slots=True)
class Capability:
    available: bool
    reason: str


@dataclass(slots=True)
class State:
    input_mode: str = "url"
    target: str = ""
    project: str = ""
    language: str = "pt-BR"
    market: str = "BR"
    max_pages: int = 100
    audits_root: str = "audits"
    device: str = "mobile"
    ai_provider: str = "none"
    ai_model: str | None = None
    ai_reasoning: str | None = None
    ai_timeout: float = DEFAULT_AI_TIMEOUT_SECONDS
    content_remediation: bool = False
    web_performance: bool = False
    web_max_pages: int = 10
    web_timeout: float = DEFAULT_WEB_PERFORMANCE_TIMEOUT_SECONDS
    field_source: str = "auto"
    lighthouse_categories: str = "performance,accessibility,best-practices,seo"
    status: str = "READY"
    current_url: str = "-"
    current_device: str = "MOBILE"
    operation: str = "LOCAL:MENU"
    error: str = ""
    audit_id: str = ""
    output: list[str] = field(default_factory=list)
    runtime_blocks: dict[str, str] = field(default_factory=dict)


def apply_environment_defaults(
    state: State,
    env: Mapping[str, str] | None = None,
    names: set[str] | None = None,
) -> tuple[str, ...]:
    """Apply CLI-equivalent environment defaults to console state."""
    environment = env if env is not None else os.environ
    issues: list[str] = []

    def active(name: str) -> bool:
        return names is None or name in names

    def boolean(name: str, default: bool) -> bool:
        raw = (environment.get(name) or "").strip()
        if not raw:
            return default
        normalized = raw.casefold()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
        issues.append(f"{name}: booleano inválido")
        return default

    if active("SEARCHGEO_DEVICE_CONTEXT"):
        raw = (environment.get("SEARCHGEO_DEVICE_CONTEXT") or "").strip().casefold()
        if not raw:
            state.device, state.current_device = "mobile", "MOBILE"
        elif raw in {"mobile", "desktop", "both"}:
            state.device, state.current_device = raw, raw.upper()
        else:
            issues.append("SEARCHGEO_DEVICE_CONTEXT: use mobile, desktop ou both")

    if active(AI_TIMEOUT_ENV):
        raw = (environment.get(AI_TIMEOUT_ENV) or "").strip()
        try:
            state.ai_timeout = DEFAULT_AI_TIMEOUT_SECONDS if not raw else float(raw)
            if state.ai_timeout <= 0:
                raise ValueError
        except ValueError:
            issues.append(f"{AI_TIMEOUT_ENV}: use número > 0")

    if active("SEARCHGEO_AI_CONTENT_REMEDIATION"):
        state.content_remediation = boolean("SEARCHGEO_AI_CONTENT_REMEDIATION", False)
    if active("SEARCHGEO_WEB_PERFORMANCE"):
        state.web_performance = boolean("SEARCHGEO_WEB_PERFORMANCE", False)

    if active("SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES"):
        raw = (environment.get("SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES") or "").strip()
        if not raw:
            state.web_max_pages = 10
        else:
            try:
                value = int(raw)
                if value < 0:
                    raise ValueError
                state.web_max_pages = value
            except ValueError:
                issues.append("SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES: use inteiro >= 0")

    if active(WEB_PERFORMANCE_TIMEOUT_ENV):
        raw = (environment.get(WEB_PERFORMANCE_TIMEOUT_ENV) or "").strip()
        if not raw:
            state.web_timeout = DEFAULT_WEB_PERFORMANCE_TIMEOUT_SECONDS
        else:
            try:
                value = float(raw)
                if value <= 0:
                    raise ValueError
                state.web_timeout = value
            except ValueError:
                issues.append(f"{WEB_PERFORMANCE_TIMEOUT_ENV}: use número > 0")

    if active("SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE"):
        raw = (environment.get("SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE") or "").strip().casefold()
        if not raw:
            state.field_source = "auto"
        elif raw in {"auto", "pagespeed", "crux", "none"}:
            state.field_source = raw
        else:
            issues.append("SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE: valor inválido")

    if active("SEARCHGEO_LIGHTHOUSE_CATEGORIES"):
        raw = (environment.get("SEARCHGEO_LIGHTHOUSE_CATEGORIES") or "").strip()
        state.lighthouse_categories = raw or "performance,accessibility,best-practices,seo"

    if state.ai_provider in PROVIDERS:
        provider_name = PROVIDERS[state.ai_provider]
        reasoning_env = provider_reasoning_env(provider_name)
        if names is None or (reasoning_env and reasoning_env in names):
            try:
                state.ai_reasoning = configured_reasoning(provider_name, environment)
            except ValueError as exc:
                issues.append(str(exc))

    return tuple(issues)


def is_secret(name: str) -> bool:
    upper = name.upper()
    return name in SECRET_NAMES or any(
        token in upper for token in ("API_KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
    )


def environment_summary(env: Mapping[str, str] | None = None) -> tuple[str, ...]:
    environment = env if env is not None else os.environ
    names = set(ENV_NAMES) | {name for name in environment if name.startswith("SEARCHGEO_")}
    items: list[str] = []
    for name in sorted(names):
        value = (environment.get(name) or "").strip()
        if not value:
            continue
        shown = "[SET]" if is_secret(name) else value.replace("\n", " ")[:48]
        items.append(f"{name}={shown")
    return tuple(items)


def _runtime_block(blocks: Mapping[str, str], provider_id: str) -> str | None:
    return blocks.get(provider_id)


def provider_capabilities(
    env: Mapping[str, str] | None = None,
    blocks: Mapping[str, str] | None = None,
) -> dict[str, Capability]:
    environment = env if env is not None else os.environ
    blocked = blocks or {}
    result: dict[str, Capability] = {"none": Capability(True, "sem IA")}
    auto_ready: list[str] = []

    for registration in _REGISTRATIONS:
        provider_id = registration.id
        key = (environment.get(registration.key_env) or "").strip()
        model = (environment.get(registration.model_env) or SIMPLE_DEFAULT_MODELS[registration.provider_name]).strip()
        block = _runtime_block(blocked, provider_id)

        if block:
            capability = Capability(False, f"bloqueado após erro: {block}")
        elif not key:
            capability = Capability(False, f"{registration.key_env} não configurada" + (f" | {registration.qualification} | explicit-only" if registration.explicit_only else ""))
        elif registration.required_key_prefixes and not key.startswith(registration.required_key_prefixes):
            prefixes = " ou ".join(registration.required_key_prefixes)
            capability = Capability(False, f"{registration.display_name} exige chave compatível ({prefixes}...)")
        elif model not in registration.supported_models:
            capability = Capability(False, f"modelo inválido em {registration.model_env}: {model}")
        else:
            try:
                effort = configured_reasoning(registration.provider_name, environment)
            except ValueError as exc:
                capability = Capability(False, str(exc))
            else:
                suffix = f" | {registration.qualification}" + (" | explicit-only" if registration.explicit_only else "")
                capability = Capability(True, f"{registration.display_name}/{model} | esforço={effort}{suffix}")

        result[provider_id] = capability
        for alias in registration.aliases:
            result[alias] = capability
        if registration.auto_eligible and capability.available:
            auto_ready.append(provider_id)

    auto_chain = " -> ".join(item.upper() for item in auto_provider_ids())
    result["auto"] = Capability(bool(auto_ready), f"{len(auto_ready)} provider(s) elegível(is); cadeia homologada {auto_chain}" if auto_ready else f"nenhum provider AUTO elegível; cadeia homologada {auto_chain}")
    return result


def _registration_by_env(name: str):
    for registration in _REGISTRATIONS:
        if name in {registration.key_env, registration.model_env, registration.endpoint_env, provider_reasoning_env(registration.provider_name)}:
            return registration
    return None


def validate_env_value(name: str, value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("valor vazio; remova a variável em vez de gravar vazio")

    registration = _registration_by_env(name)
    if registration is not None:
        if name == registration.key_env:
            if registration.required_key_prefixes and not value.startswith(registration.required_key_prefixes):
                prefixes = " ou ".join(registration.required_key_prefixes)
                raise ValueError(f"{registration.display_name} exige chave compatível ({prefixes}...)")
            return value
        if name == registration.model_env:
            if value not in registration.supported_models:
                raise ValueError(f"modelos suportados: {', '.join(registration.supported_models)}")
            return value
        if name == provider_reasoning_env(registration.provider_name):
            value = value.upper()
            if value not in REASONING_OPTIONS[registration.provider_name]:
                raise ValueError("reasoning effort não suportado; use " + ", ".join(REASONING_OPTIONS[registration.provider_name]))
            return value
        if name == registration.endpoint_env:
            return value

    if name in {"SEARCHGEO_AI_CONTENT_REMEDIATION", "SEARCHGEO_WEB_PERFORMANCE"}:
        if value.casefold() not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
            raise ValueError("booleano inválido")
    elif name == "SEARCHGEO_DEVICE_CONTEXT":
        value = value.casefold()
        if value not in {"mobile", "desktop", "both"}:
            raise ValueError("use mobile, desktop ou both")
    elif name in {AI_TIMEOUT_ENV, WEB_PERFORMANCE_TIMEOUT_ENV}:
        if float(value) <= 0:
            raise ValueError("valor deve ser > 0")
    elif name == "SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES":
        if int(value) < 0:
            raise ValueError("valor deve ser >= 0")
    elif name == "SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE":
        value = value.casefold()
        if value not in {"auto", "pagespeed", "crux", "none"}:
            raise ValueError("use auto, pagespeed, crux ou none")
        if value == "crux" and not (os.environ.get("SEARCHGEO_CRUX_API_KEY") or "").strip():
            raise ValueError("crux exige SEARCHGEO_CRUX_API_KEY")
    elif name == "PLAYWRIGHT_CHROMIUM_EXECUTABLE" and not Path(value).is_file():
        raise ValueError("arquivo Chromium configurado não existe")
    return value


def _capability_for_selection(selection: str, env: Mapping[str, str], blocks: Mapping[str, str]) -> Capability | None:
    capabilities = provider_capabilities(env, blocks)
    normalized = selection.strip().casefold()
    registration = get_provider_registration(normalized)
    key = registration.id if registration is not None else normalized
    return capabilities.get(key)


def preflight(state: State, env: Mapping[str, str] | None = None) -> tuple[str, ...]:
    environment = env if env is not None else os.environ
    if state.max_pages <= 0 or state.web_max_pages < 0 or state.web_timeout <= 0 or state.ai_timeout <= 0:
        raise ValueError("limites/timeout inválidos")
    if state.input_mode == "url":
        if not state.target.strip():
            raise ValueError("informe uma URL/domínio")
        targets = (validate_target(state.target),)
    elif state.input_mode == "file":
        path = Path(state.target)
        if not path.is_file():
            raise ValueError(f"TXT não encontrado: {path}")
        targets = tuple(validate_target(line.strip()) for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#"))
        if not targets:
            raise ValueError("TXT não contém targets")
    else:
        raise ValueError("modo de entrada inválido")
    normalized = tuple(dict.fromkeys(normalize_url(item) for item in targets))
    if len({normalized_origin(item) for item in normalized}) != 1:
        raise ValueError("todos os targets devem pertencer à mesma origem normalizada")
    if state.input_mode == "file" and len(normalized) > state.max_pages:
        raise ValueError(f"TXT possui {len(normalized)} URLs únicas e max-pages={state.max_pages}")
    capability = _capability_for_selection(state.ai_provider, environment, state.runtime_blocks)
    if not capability or not capability.available:
        reason = capability.reason if capability else "inválido"
        raise ValueError(f"provider {state.ai_provider} indisponível: {reason}")
    if state.ai_provider == "none" and state.content_remediation:
        raise ValueError("remediação textual exige provider de IA apto")
    if state.ai_provider == "auto" and state.ai_model:
        raise ValueError("AUTO não aceita --ai-model")
    if state.web_performance and state.field_source == "crux" and not (environment.get("SEARCHGEO_CRUX_API_KEY") or "").strip():
        raise ValueError("field source crux exige SEARCHGEO_CRUX_API_KEY")
    browser = (environment.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or "").strip()
    if browser and not Path(browser).is_file():
        raise ValueError("PLAYWRIGHT_CHROMIUM_EXECUTABLE não existe")
    return normalized


def build_command(state: State) -> list[str]:
    command = [sys.executable, "-m", "searchgeo", "audit"]
    command += ["--urls-file", state.target] if state.input_mode == "file" else [state.target]
    if state.project:
        command += ["--project", state.project]
    command += ["--language", state.language, "--market", state.market, "--max-pages", str(state.max_pages), "--audits-root", state.audits_root, "--device-context", state.device, "--ai-provider", state.ai_provider]
    if get_provider_registration(state.ai_provider) is not None and state.ai_model:
        command += ["--ai-model", state.ai_model]
    command += ["--ai-content-remediation" if state.content_remediation else "--no-ai-content-remediation"]
    command += ["--web-performance" if state.web_performance else "--no-web-performance"]
    if state.web_performance:
        command += ["--web-performance-max-pages", str(state.web_max_pages), "--web-performance-timeout-seconds", str(state.web_timeout), "--web-performance-field-source", state.field_source, "--lighthouse-categories", state.lighthouse_categories]
    return command
