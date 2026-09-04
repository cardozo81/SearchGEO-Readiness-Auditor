"""Configuration and preflight rules for the optional interactive console."""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import sys
from typing import Mapping

from searchgeo.cli import validate_target
from searchgeo.m18_ai import DEFAULT_MODELS, KEY_ENV, MODEL_ENV, SUPPORTED_MODELS
from searchgeo.url_utils import normalize_url, normalized_origin

ENV_NAMES = (
    "SEARCHGEO_CONFIG", "SEARCHGEO_LOG_LEVEL", "SEARCHGEO_DEVICE_CONTEXT",
    "SEARCHGEO_AI_TIMEOUT_SECONDS", "SEARCHGEO_AI_CONTENT_REMEDIATION",
    "OPENAI_API_KEY", "DEEPSEEK_API_KEY", "MIMO_API_KEY",
    "SEARCHGEO_OPENAI_MODEL", "SEARCHGEO_DEEPSEEK_MODEL", "SEARCHGEO_MIMO_MODEL",
    "SEARCHGEO_OPENAI_REASONING_EFFORT", "SEARCHGEO_DEEPSEEK_REASONING_EFFORT",
    "SEARCHGEO_MIMO_REASONING_EFFORT", "SEARCHGEO_WEB_PERFORMANCE",
    "SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES", "SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS",
    "SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE", "SEARCHGEO_LIGHTHOUSE_CATEGORIES",
    "SEARCHGEO_PAGESPEED_API_KEY", "SEARCHGEO_CRUX_API_KEY", "PLAYWRIGHT_CHROMIUM_EXECUTABLE",
)
SECRET_NAMES = frozenset({
    "OPENAI_API_KEY", "DEEPSEEK_API_KEY", "MIMO_API_KEY",
    "SEARCHGEO_PAGESPEED_API_KEY", "SEARCHGEO_CRUX_API_KEY",
})
PROVIDERS = {"openai": "OPENAI", "deepseek": "DEEPSEEK", "mimo": "MIMO"}


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
    content_remediation: bool = False
    web_performance: bool = False
    web_max_pages: int = 10
    web_timeout: float = 60.0
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


def is_secret(name: str) -> bool:
    upper = name.upper()
    return name in SECRET_NAMES or any(token in upper for token in ("API_KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL"))


def environment_summary(env: Mapping[str, str] | None = None) -> tuple[str, ...]:
    environment = env if env is not None else os.environ
    names = set(ENV_NAMES) | {name for name in environment if name.startswith("SEARCHGEO_")}
    items: list[str] = []
    for name in sorted(names):
        value = (environment.get(name) or "").strip()
        if not value:
            continue
        shown = "[SET]" if is_secret(name) else value.replace("\n", " ")[:48]
        items.append(f"{name}={shown}")
    return tuple(items)


def provider_capabilities(
    env: Mapping[str, str] | None = None,
    blocks: Mapping[str, str] | None = None,
) -> dict[str, Capability]:
    environment = env if env is not None else os.environ
    blocked = blocks or {}
    result = {"none": Capability(True, "sem IA")}
    ready = 0
    for selection, provider in PROVIDERS.items():
        key_name, model_name = KEY_ENV[provider], MODEL_ENV[provider]
        key = (environment.get(key_name) or "").strip()
        model = (environment.get(model_name) or DEFAULT_MODELS[provider]).strip()
        reasoning_name = f"SEARCHGEO_{provider}_REASONING_EFFORT"
        reasoning = (environment.get(reasoning_name) or "HIGH").strip().upper()
        allowed_reasoning = (
            {"NONE", "LOW", "MEDIUM", "HIGH"}
            if provider == "MIMO"
            else {"NONE", "LOW", "MEDIUM", "HIGH", "XHIGH", "MAX"}
        )
        if selection in blocked:
            result[selection] = Capability(False, f"bloqueado após erro: {blocked[selection]}")
        elif not key:
            result[selection] = Capability(False, f"{key_name} não configurada")
        elif provider == "MIMO" and not key.startswith("sk-"):
            result[selection] = Capability(False, "MIMO exige chave PAYG sk-...; tp-... não é suportada")
        elif model not in SUPPORTED_MODELS[provider]:
            result[selection] = Capability(False, f"modelo inválido em {model_name}: {model}")
        elif reasoning not in allowed_reasoning:
            result[selection] = Capability(False, f"{reasoning_name} inválido: {reasoning}")
        else:
            result[selection] = Capability(True, f"{provider}/{model}")
            ready += 1
    result["auto"] = Capability(
        ready > 0,
        f"{ready} provider(s) elegível(is)" if ready else "nenhum provider elegível",
    )
    return result


def validate_env_value(name: str, value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("valor vazio; remova a variável em vez de gravar vazio")
    if name in {"SEARCHGEO_AI_CONTENT_REMEDIATION", "SEARCHGEO_WEB_PERFORMANCE"}:
        if value.casefold() not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
            raise ValueError("booleano inválido")
    elif name == "SEARCHGEO_DEVICE_CONTEXT":
        value = value.casefold()
        if value not in {"mobile", "desktop", "both"}:
            raise ValueError("use mobile, desktop ou both")
    elif name in {"SEARCHGEO_AI_TIMEOUT_SECONDS", "SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS"}:
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
    elif name.endswith("_REASONING_EFFORT"):
        value = value.upper()
        allowed = (
            {"NONE", "LOW", "MEDIUM", "HIGH"}
            if "MIMO" in name
            else {"NONE", "LOW", "MEDIUM", "HIGH", "XHIGH", "MAX"}
        )
        if value not in allowed:
            raise ValueError("reasoning effort não suportado")
    elif name == "MIMO_API_KEY" and not value.startswith("sk-"):
        raise ValueError("MiMo exige chave PAYG sk-...; tp-... não é suportada")
    elif name == "PLAYWRIGHT_CHROMIUM_EXECUTABLE" and not Path(value).is_file():
        raise ValueError("arquivo Chromium configurado não existe")
    else:
        for provider, model_env in MODEL_ENV.items():
            if name == model_env and value not in SUPPORTED_MODELS[provider]:
                raise ValueError(f"modelos suportados: {', '.join(SUPPORTED_MODELS[provider])}")
    return value


def preflight(state: State, env: Mapping[str, str] | None = None) -> tuple[str, ...]:
    environment = env if env is not None else os.environ
    if state.max_pages <= 0 or state.web_max_pages < 0 or state.web_timeout <= 0:
        raise ValueError("limites/timeout inválidos")
    if state.input_mode == "url":
        if not state.target.strip():
            raise ValueError("informe uma URL/domínio")
        targets = (validate_target(state.target),)
    elif state.input_mode == "file":
        path = Path(state.target)
        if not path.is_file():
            raise ValueError(f"TXT não encontrado: {path}")
        targets = tuple(
            validate_target(line.strip())
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
        if not targets:
            raise ValueError("TXT não contém targets")
    else:
        raise ValueError("modo de entrada inválido")
    normalized = tuple(dict.fromkeys(normalize_url(item) for item in targets))
    if len({normalized_origin(item) for item in normalized}) != 1:
        raise ValueError("todos os targets devem pertencer à mesma origem normalizada")
    if state.input_mode == "file" and len(normalized) > state.max_pages:
        raise ValueError(f"TXT possui {len(normalized)} URLs únicas e max-pages={state.max_pages}")
    capability = provider_capabilities(environment, state.runtime_blocks).get(state.ai_provider)
    if not capability or not capability.available:
        raise ValueError(
            f"provider {state.ai_provider} indisponível: "
            f"{capability.reason if capability else 'inválido'}"
        )
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
    command += [
        "--language", state.language,
        "--market", state.market,
        "--max-pages", str(state.max_pages),
        "--audits-root", state.audits_root,
        "--device-context", state.device,
        "--ai-provider", state.ai_provider,
    ]
    if state.ai_provider in PROVIDERS and state.ai_model:
        command += ["--ai-model", state.ai_model]
    command += ["--ai-content-remediation" if state.content_remediation else "--no-ai-content-remediation"]
    command += ["--web-performance" if state.web_performance else "--no-web-performance"]
    if state.web_performance:
        command += [
            "--web-performance-max-pages", str(state.web_max_pages),
            "--web-performance-timeout-seconds", str(state.web_timeout),
            "--web-performance-field-source", state.field_source,
            "--lighthouse-categories", state.lighthouse_categories,
        ]
    return command
