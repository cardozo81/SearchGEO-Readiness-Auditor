"""Friendly menu for SearchGEO audit execution."""
from __future__ import annotations

from getpass import getpass
import os

from searchgeo.console_config import (
    ENV_NAMES,
    KEY_ENV,
    MODEL_ENV,
    DEFAULT_MODELS,
    PROVIDERS,
    SUPPORTED_MODELS,
    State,
    apply_environment_defaults,
    is_secret,
    preflight,
    provider_capabilities,
    validate_env_value,
)
from searchgeo.console_runtime import render_header, run_audit_from_console


def _select(title: str, options: list[tuple[str, bool, str]]) -> str | None:
    print(title)
    allowed: dict[str, str] = {}
    for index, (value, available, reason) in enumerate(options, 1):
        marker = "OK" if available else "INDISPONÍVEL"
        print(f" {index}. {value:<12} [{marker}] {reason}")
        if available:
            allowed[str(index)] = value
    print(" 0. cancelar")
    while True:
        raw = input("Escolha: ").strip()
        if raw == "0":
            return None
        if raw in allowed:
            return allowed[raw]
        print("Opção indisponível ou inválida.")


def _environment_menu(state: State) -> None:
    while True:
        render_header(state)
        for index, name in enumerate(ENV_NAMES, 1):
            value = os.environ.get(name)
            shown = "<não definida>" if not value else "[SET]" if is_secret(name) else value
            print(f"{index:2d}. {name:<44} {shown}")
        action = input("\nS=setar/alterar | R=remover | V=voltar: ").strip().upper()
        if action == "V":
            return
        if action not in {"S", "R"}:
            continue
        try:
            name = ENV_NAMES[int(input("Número: ").strip()) - 1]
        except (ValueError, IndexError):
            state.error = "variável inválida"
            continue
        if action == "R":
            os.environ.pop(name, None)
            state.error = ""
        else:
            raw = getpass(f"{name}: ") if is_secret(name) else input(f"{name}: ")
            try:
                os.environ[name] = validate_env_value(name, raw)
                state.error = ""
            except (ValueError, OverflowError) as exc:
                state.error = str(exc)
                continue
        issues = apply_environment_defaults(state, names={name})
        state.error = "; ".join(issues)
        for selection, provider in PROVIDERS.items():
            if KEY_ENV[provider] == name:
                state.runtime_blocks.pop(selection, None)


def _configure(state: State, choice: str) -> None:
    if choice == "1":
        mode = _select(
            "Fonte (default: URL única)",
            [("url", True, "URL/domínio"), ("file", True, "TXT UTF-8, uma URL por linha")],
        )
        if mode:
            state.input_mode = mode
            state.target = input("URL/domínio: " if mode == "url" else "Caminho TXT: ").strip()
            state.current_url = state.target or "-"
    elif choice == "2":
        state.project = input("Projeto (vazio=auto): ").strip()
    elif choice == "3":
        value = _select(
            "Dispositivo",
            [("mobile", True, "default público"), ("desktop", True, "somente desktop"), ("both", True, "mobile + desktop")],
        )
        if value:
            state.device, state.current_device = value, value.upper()
    elif choice == "4":
        capabilities = provider_capabilities(blocks=state.runtime_blocks)
        value = _select(
            "Provider de IA",
            [(name, capabilities[name].available, capabilities[name].reason) for name in ("none", "openai", "deepseek", "mimo", "auto")],
        )
        if value:
            state.ai_provider, state.ai_model = value, None
            if value == "none":
                state.content_remediation = False
            elif value in PROVIDERS:
                provider = PROVIDERS[value]
                default = os.environ.get(MODEL_ENV[provider], DEFAULT_MODELS[provider])
                chosen = _select(
                    f"Modelo {provider}",
                    [(model, True, "default" if model == default else "") for model in SUPPORTED_MODELS[provider]],
                )
                state.ai_model = chosen or default
    elif choice == "5":
        capability = provider_capabilities(blocks=state.runtime_blocks)[state.ai_provider]
        if state.ai_provider == "none" or not capability.available:
            state.content_remediation, state.error = False, "remediação IA indisponível"
        else:
            state.content_remediation = input("Remediação textual IA? [s/N]: ").strip().casefold() == "s"
    elif choice == "6":
        state.web_performance = input("Web Performance? [s/N]: ").strip().casefold() == "s"
        if state.web_performance:
            crux_available = bool((os.environ.get("SEARCHGEO_CRUX_API_KEY") or "").strip())
            value = _select(
                "Field data",
                [
                    ("auto", True, "default"),
                    ("pagespeed", True, "PageSpeed"),
                    ("crux", crux_available, "exige SEARCHGEO_CRUX_API_KEY"),
                    ("none", True, "somente Lighthouse lab"),
                ],
            )
            if value:
                state.field_source = value
    elif choice == "7":
        try:
            value = int(input("max-pages (>0): "))
            if value <= 0:
                raise ValueError
            state.max_pages = value
            state.error = ""
        except ValueError:
            state.error = "max-pages inválido"
    elif choice == "8":
        try:
            value = int(input("WebPerf max-pages (>=0): "))
            if value < 0:
                raise ValueError
            state.web_max_pages = value
            state.error = ""
        except ValueError:
            state.error = "WebPerf max-pages inválido"
    elif choice == "9":
        state.language = input(f"Idioma [{state.language}]: ").strip() or state.language
        state.market = input(f"Mercado [{state.market}]: ").strip() or state.market
    elif choice == "10":
        state.audits_root = input(f"Raiz [{state.audits_root}]: ").strip() or state.audits_root


def _execution_readiness(state: State) -> tuple[bool, str]:
    try:
        preflight(state)
    except (OSError, ValueError, UnicodeError) as exc:
        return False, str(exc)
    return True, "configuração válida"


def _menu(state: State) -> str:
    render_header(state)
    capability = provider_capabilities(blocks=state.runtime_blocks)[state.ai_provider]
    print(f"1. Entrada               : {'URL única' if state.input_mode == 'url' else 'TXT'} | {state.target or '<não informada>'}")
    print(f"2. Projeto               : {state.project or '<auto>'}")
    print(f"3. Dispositivo           : {state.device}")
    print(f"4. IA                    : {state.ai_provider} [{'apto' if capability.available else 'indisponível'}] | {state.ai_model or '<default>'}")
    print(f"5. Remediação textual IA : {'on' if state.content_remediation else 'off'}")
    print(f"6. Web Performance       : {'on' if state.web_performance else 'off'} | field={state.field_source}")
    print(f"7. max-pages             : {state.max_pages}")
    print(f"8. WebPerf max-pages     : {state.web_max_pages}")
    print(f"9. Idioma / mercado      : {state.language} / {state.market}")
    print(f"10. Raiz auditorias      : {state.audits_root}")
    ready, reason = _execution_readiness(state)
    marker = "APTO" if ready else "BLOQUEADO"
    print(f"\nE. Variáveis de ambiente | R. Executar [{marker}] {reason} | Q. Sair")
    return input("Escolha: ").strip().upper()


def main() -> int:
    state = State()
    issues = apply_environment_defaults(state)
    state.error = "; ".join(issues)
    while True:
        choice = _menu(state)
        if choice == "Q":
            return 0
        if choice == "E":
            _environment_menu(state)
            continue
        if choice == "R":
            ready, reason = _execution_readiness(state)
            if not ready:
                state.status, state.operation, state.error = "PRECHECK_BLOCKED", "LOCAL:PRECHECK", reason
                continue
            run_audit_from_console(state)
            input("\nENTER para voltar ao menu...")
            state.status, state.operation, state.error = "READY", "LOCAL:MENU", ""
            continue
        _configure(state, choice)


if __name__ == "__main__":
    raise SystemExit(main())
