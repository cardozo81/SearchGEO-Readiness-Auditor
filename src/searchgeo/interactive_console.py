"""Friendly menu for SearchGEO audit execution."""
from __future__ import annotations

from getpass import getpass
import os

from searchgeo.console_artifacts import artifact_status, open_audit_folder, open_report
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
from searchgeo.console_help import (
    menu_cost_badges,
    render_environment_help,
    render_help,
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


def _environment_help_menu() -> None:
    try:
        raw = input("Número da variável para ajuda [0=todas]: ").strip()
        if raw == "0":
            for name in ENV_NAMES:
                render_environment_help(name)
        else:
            name = ENV_NAMES[int(raw) - 1]
            render_environment_help(name)
    except (ValueError, IndexError):
        print("Variável inválida.")
    input("\nENTER para voltar...")


def _environment_menu(state: State) -> None:
    while True:
        render_header(state)
        print("Variáveis de ambiente — valores sensíveis nunca são exibidos\n")
        for index, name in enumerate(ENV_NAMES, 1):
            value = os.environ.get(name)
            shown = "<não definida>" if not value else "[SET]" if is_secret(name) else value
            print(f"{index:2d}. {name:<44} {shown}")
        action = input("\nS=setar/alterar | R=remover | H=ajuda/custo | V=voltar: ").strip().upper()
        if action == "V":
            return
        if action == "H":
            _environment_help_menu()
            continue
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
            [("mobile", True, "default público"), ("desktop", True, "somente desktop"), ("both", True, "mobile + desktop; pode aumentar consumo")],
        )
        if value:
            state.device, state.current_device = value, value.upper()
    elif choice == "4":
        capabilities = provider_capabilities(blocks=state.runtime_blocks)
        value = _select(
            "Provider de IA — providers externos podem gerar custo por uso",
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
                    f"Modelo {provider} — modelos podem ter preços diferentes no provider",
                    [(model, True, "default" if model == default else "") for model in SUPPORTED_MODELS[provider]],
                )
                state.ai_model = chosen or default
    elif choice == "5":
        capability = provider_capabilities(blocks=state.runtime_blocks)[state.ai_provider]
        if state.ai_provider == "none" or not capability.available:
            state.content_remediation, state.error = False, "remediação IA indisponível"
        else:
            state.content_remediation = input(
                "Remediação textual IA? Pode gerar chamadas/custo adicionais [s/N]: "
            ).strip().casefold() == "s"
    elif choice == "6":
        state.web_performance = input(
            "Web Performance? Usa APIs/quota externa PageSpeed/CrUX [s/N]: "
        ).strip().casefold() == "s"
        if state.web_performance:
            crux_available = bool((os.environ.get("SEARCHGEO_CRUX_API_KEY") or "").strip())
            value = _select(
                "Field data",
                [
                    ("auto", True, "default; pode consultar fontes externas conforme disponibilidade"),
                    ("pagespeed", True, "PageSpeed"),
                    ("crux", crux_available, "exige SEARCHGEO_CRUX_API_KEY"),
                    ("none", True, "somente Lighthouse lab"),
                ],
            )
            if value:
                state.field_source = value
    elif choice == "7":
        try:
            value = int(input("max-pages (>0; maior valor aumenta teto potencial de consumo): "))
            if value <= 0:
                raise ValueError
            state.max_pages = value
            state.error = ""
        except ValueError:
            state.error = "max-pages inválido"
    elif choice == "8":
        try:
            value = int(input("WebPerf max-pages (>=0; limita volume de API externa): "))
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


def _artifact_action(state: State, action: str) -> None:
    if action == "P":
        ok, detail = open_audit_folder(state)
        state.operation = "LOCAL:OPEN_AUDIT_FOLDER"
    else:
        ok, detail = open_report(state)
        state.operation = "LOCAL:OPEN_REPORT"
    state.error = "" if ok else detail
    render_header(state)
    print(("Aberto: " if ok else "Não foi possível abrir: ") + detail)
    input("\nENTER para continuar...")


def _post_run_actions(state: State) -> bool:
    """Return True when the user chooses to exit the console."""
    while True:
        render_header(state)
        workspace, report = artifact_status(state)
        if state.audit_id:
            print(f"Audit ID    : {state.audit_id}")
        print("\nAções da auditoria desta sessão")
        print(f" P. Abrir pasta da auditoria [{'OK' if workspace else 'INDISPONÍVEL'}]")
        print(f" I. Abrir relatório HTML   [{'OK' if report else 'INDISPONÍVEL'}]")
        print(" M. Voltar ao menu")
        print(" Q. Sair")
        choice = input("Escolha: ").strip().upper()
        if choice == "Q":
            return True
        if choice == "M":
            return False
        if choice == "P" and workspace:
            _artifact_action(state, "P")
        elif choice == "I" and report:
            _artifact_action(state, "I")
        elif choice in {"P", "I"}:
            state.error = "artefato ainda não disponível para esta auditoria"


def _menu(state: State) -> str:
    render_header(state)
    capability = provider_capabilities(blocks=state.runtime_blocks)[state.ai_provider]
    badges = menu_cost_badges(state)
    print(f"1. Entrada               : {'URL única' if state.input_mode == 'url' else 'TXT'} | {state.target or '<não informada>'}")
    print(f"2. Projeto               : {state.project or '<auto>'}")
    print(f"3. Dispositivo           : {state.device}{badges['device']}")
    print(f"4. IA                    : {state.ai_provider} [{'apto' if capability.available else 'indisponível'}] | {state.ai_model or '<default>'}{badges['ai']}")
    print(f"5. Remediação textual IA : {'on' if state.content_remediation else 'off'}{badges['remediation']}")
    print(f"6. Web Performance       : {'on' if state.web_performance else 'off'} | field={state.field_source}{badges['web']}")
    print(f"7. max-pages             : {state.max_pages}{badges['max_pages']}")
    print(f"8. WebPerf max-pages     : {state.web_max_pages}{badges['web_max_pages']}")
    print(f"9. Idioma / mercado      : {state.language} / {state.market}")
    print(f"10. Raiz auditorias      : {state.audits_root}")
    ready, reason = _execution_readiness(state)
    marker = "APTO" if ready else "BLOQUEADO"
    print(f"\nH. Ajuda / custos | E. Variáveis de ambiente | R. Executar [{marker}] {reason} | Q. Sair")
    workspace, report = artifact_status(state)
    if workspace or report:
        print(
            f"P. Abrir última pasta [{'OK' if workspace else 'INDISPONÍVEL'}] | "
            f"I. Abrir último relatório [{'OK' if report else 'INDISPONÍVEL'}]"
        )
    return input("Escolha: ").strip().upper()


def main() -> int:
    state = State()
    issues = apply_environment_defaults(state)
    state.error = "; ".join(issues)
    while True:
        choice = _menu(state)
        if choice == "Q":
            return 0
        if choice == "H":
            render_help(state)
            input("\nENTER para voltar ao menu...")
            continue
        if choice == "E":
            _environment_menu(state)
            continue
        if choice in {"P", "I"}:
            _artifact_action(state, choice)
            continue
        if choice == "R":
            ready, reason = _execution_readiness(state)
            if not ready:
                state.status, state.operation, state.error = "PRECHECK_BLOCKED", "LOCAL:PRECHECK", reason
                continue
            run_audit_from_console(state)
            if _post_run_actions(state):
                return 0
            state.status, state.operation, state.error = "READY", "LOCAL:MENU", ""
            continue
        _configure(state, choice)


if __name__ == "__main__":
    raise SystemExit(main())
