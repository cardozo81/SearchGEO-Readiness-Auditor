"""Friendly menu for SearchGEO audit execution."""
from __future__ import annotations

from getpass import getpass
import os

from searchgeo.console_artifacts import artifact_status, open_audit_folder, open_report
from searchgeo.console_config import (
    DEFAULT_MODELS,
    ENV_NAMES,
    KEY_ENV,
    MODEL_ENV,
    PROVIDERS,
    PROVIDER_MENU_CHOICES,
    SUPPORTED_MODELS,
    State,
    apply_environment_defaults,
    is_secret,
    preflight,
    provider_capabilities,
    validate_env_value,
)
from searchgeo.console_cost import actual_usage, estimate_exposure
from searchgeo.console_help import menu_cost_badges, render_environment_help, render_help
from searchgeo.console_runtime import render_header, run_audit_from_console
from searchgeo.console_ui import (
    CYAN,
    DIM,
    GREEN,
    RED,
    YELLOW,
    availability_badge,
    bool_badge,
    cost_color,
    paint,
)


def _select(state: State, title: str, options: list[tuple[str, bool, str]]) -> str | None:
    render_header(state)
    print(title)
    allowed: dict[str, str] = {}
    for index, (value, available, reason) in enumerate(options, 1):
        marker = availability_badge(available)
        reason_text = paint(reason, CYAN if available else RED)
        print(f" {index}. {value:<18} [{marker}] {reason_text}")
        if available:
            allowed[str(index)] = value
    print(" 0. cancelar")
    while True:
        raw = input("Escolha: ").strip()
        if raw == "0":
            return None
        if raw in allowed:
            return allowed[raw]
        print(paint("Opção indisponível ou inválida.", RED, bold=True))


def _environment_help_menu(state: State) -> None:
    render_header(state)
    print("AJUDA DE VARIÁVEIS — selecione uma variável ou 0 para todas\n")
    for index, name in enumerate(ENV_NAMES, 1):
        print(f"{index:2d}. {name}")
    try:
        raw = input("\nNúmero [0=todas]: ").strip()
        render_header(state)
        print("AJUDA DE VARIÁVEIS\n")
        if raw == "0":
            for name in ENV_NAMES:
                render_environment_help(name)
        else:
            render_environment_help(ENV_NAMES[int(raw) - 1])
    except (ValueError, IndexError):
        print(paint("Variável inválida.", RED, bold=True))
    input("\nENTER para voltar...")


def _environment_menu(state: State) -> None:
    while True:
        render_header(state)
        print("Variáveis de ambiente — valores sensíveis nunca são exibidos\n")
        for index, name in enumerate(ENV_NAMES, 1):
            value = os.environ.get(name)
            if not value:
                shown = paint("<não definida>", DIM)
            elif is_secret(name):
                shown = paint("[SET]", GREEN, bold=True)
            elif value.strip().casefold() in {"true", "1", "yes", "on"}:
                shown = paint(value, GREEN, bold=True)
            elif value.strip().casefold() in {"false", "0", "no", "off"}:
                shown = paint(value, DIM)
            else:
                shown = paint(value, CYAN)
            print(f"{index:2d}. {name:<44} {shown}")
        action = input(
            "\nS=setar/alterar | R=remover | H=ajuda/custo | V=voltar: "
        ).strip().upper()
        if action == "V":
            return
        if action == "H":
            _environment_help_menu(state)
            continue
        if action not in {"S", "R"}:
            continue
        try:
            selected = int(input("Número: ").strip()) - 1
            name = ENV_NAMES[selected]
        except (ValueError, IndexError):
            state.error = "variável inválida"
            continue

        render_header(state)
        print(f"Variável selecionada: {name}\n")
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
    render_header(state)
    if choice == "1":
        mode = _select(
            state,
            "Fonte (default: URL única)",
            [
                ("url", True, "URL/domínio; seed de crawl"),
                ("file", True, "TXT UTF-8; uma URL por linha"),
            ],
        )
        if mode:
            render_header(state)
            print(f"Entrada selecionada: {mode}\n")
            state.input_mode = mode
            state.target = input(
                "URL/domínio: " if mode == "url" else "Caminho TXT: "
            ).strip()
            state.current_url = state.target or "-"
    elif choice == "2":
        state.project = input("Projeto (vazio=auto): ").strip()
    elif choice == "3":
        value = _select(
            state,
            "Dispositivo",
            [
                ("mobile", True, "default"),
                ("desktop", True, "somente desktop"),
                ("both", True, "mobile + desktop; multiplica volume"),
            ],
        )
        if value:
            state.device, state.current_device = value, value.upper()
    elif choice == "4":
        capabilities = provider_capabilities(blocks=state.runtime_blocks)
        value = _select(
            state,
            "Provider de IA — lista dinâmica do registry canônico; "
            "providers externos podem gerar cobrança por uso",
            [
                (name, capabilities[name].available, capabilities[name].reason)
                for name in PROVIDER_MENU_CHOICES
            ],
        )
        if value:
            state.ai_provider, state.ai_model = value, None
            if value == "none":
                state.content_remediation = False
            elif value in PROVIDERS:
                provider = PROVIDERS[value]
                default = os.environ.get(
                    MODEL_ENV[provider],
                    DEFAULT_MODELS[provider],
                )
                chosen = _select(
                    state,
                    f"Modelo {provider} — preços podem variar por modelo",
                    [
                        (
                            model,
                            True,
                            "default" if model == default else "suportado",
                        )
                        for model in SUPPORTED_MODELS[provider]
                    ],
                )
                state.ai_model = chosen or default
    elif choice == "5":
        capability = provider_capabilities(
            blocks=state.runtime_blocks
        )[state.ai_provider]
        if state.ai_provider == "none" or not capability.available:
            state.content_remediation, state.error = (
                False,
                "remediação IA indisponível",
            )
        else:
            state.content_remediation = (
                input(
                    "Remediação textual IA? Pode gerar chamadas/custo adicionais [s/N]: "
                )
                .strip()
                .casefold()
                == "s"
            )
    elif choice == "6":
        state.web_performance = (
            input(
                "Web Performance? Usa API/quota externa PageSpeed/CrUX [s/N]: "
            )
            .strip()
            .casefold()
            == "s"
        )
        if state.web_performance:
            crux_available = bool(
                (os.environ.get("SEARCHGEO_CRUX_API_KEY") or "").strip()
            )
            value = _select(
                state,
                "Field data",
                [
                    (
                        "auto",
                        True,
                        "PageSpeed + CrUX direto quando necessário/disponível",
                    ),
                    ("pagespeed", True, "PageSpeed"),
                    ("crux", crux_available, "exige SEARCHGEO_CRUX_API_KEY"),
                    (
                        "none",
                        True,
                        "sem field data; Lighthouse lab permanece",
                    ),
                ],
            )
            if value:
                state.field_source = value
    elif choice == "7":
        try:
            value = int(
                input(
                    "max-pages (>0; maior valor aumenta teto potencial de consumo): "
                )
            )
            if value <= 0:
                raise ValueError
            state.max_pages = value
            state.error = ""
        except ValueError:
            state.error = "max-pages inválido"
    elif choice == "8":
        try:
            value = int(
                input(
                    "WebPerf max-pages (>=0; 0=todas as páginas auditadas): "
                )
            )
            if value < 0:
                raise ValueError
            state.web_max_pages = value
            state.error = ""
        except ValueError:
            state.error = "WebPerf max-pages inválido"
    elif choice == "9":
        state.language = (
            input(f"Idioma [{state.language}]: ").strip() or state.language
        )
        state.market = input(f"Mercado [{state.market}]: ").strip() or state.market
    elif choice == "10":
        state.audits_root = (
            input(f"Raiz [{state.audits_root}]: ").strip() or state.audits_root
        )


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
    print(
        (
            paint("Aberto: ", GREEN, bold=True)
            if ok
            else paint("Não foi possível abrir: ", RED, bold=True)
        )
        + detail
    )
    input("\nENTER para continuar...")


def _render_actual_usage(state: State) -> None:
    workspace, _ = artifact_status(state)
    usage = actual_usage(workspace)
    print("\nCONSUMO REAL / ESTIMADO PERSISTIDO")
    print("-" * 100)
    if usage is None:
        print(
            paint(
                "Telemetria de consumo indisponível para esta auditoria.",
                YELLOW,
            )
        )
        return
    print(
        f"Tentativas IA       : {usage.ai_attempts} "
        f"(sucesso: {usage.ai_successes})"
    )
    print(f"Tokens input        : {usage.input_tokens:,}")
    print(f"Tokens input cache  : {usage.cached_input_tokens:,}")
    print(f"Tokens output       : {usage.output_tokens:,}")
    print(f"Tokens reasoning    : {usage.reasoning_tokens:,}")
    print(
        f"Tokens total        : "
        f"{paint(f'{usage.total_tokens:,}', CYAN, bold=True)}"
    )
    if usage.costs:
        rendered_costs = " | ".join(
            f"{currency} {amount:.8f}"
            for currency, amount in usage.costs
        )
        print(
            f"Custo IA estimado   : "
            f"{paint(rendered_costs, YELLOW, bold=True)}"
        )
    elif usage.ai_attempts:
        print(
            "Custo IA estimado   : não disponível com dados de "
            "pricing/tokens persistidos"
        )
    else:
        print("Custo IA estimado   : 0 (nenhuma tentativa de IA persistida)")
    if usage.unpriced_ai_attempts:
        print(
            paint(
                f"Atenção: {usage.unpriced_ai_attempts} tentativa(s) IA "
                "possuem tokens mas não custo estimável persistido.",
                YELLOW,
                bold=True,
            )
        )
    if usage.web_external_calls:
        services = ", ".join(
            f"{service}={count}" for service, count in usage.web_services
        )
        print(f"Chamadas M21        : {usage.web_external_calls} ({services})")
        print(
            "Custo M21 monetário : não presumido; o console contabiliza "
            "chamadas/quota sem inventar preço."
        )
    else:
        print("Chamadas M21        : 0")
    print(
        "Observação           : custos são estimativas técnicas dos adapters, "
        "não invoice do provider."
    )


def _post_run_actions(state: State) -> bool:
    """Return True when the user chooses to exit the console."""
    while True:
        render_header(state)
        workspace, report = artifact_status(state)
        if state.audit_id:
            print(f"Audit ID    : {state.audit_id}")
        _render_actual_usage(state)
        print("\nAÇÕES DA AUDITORIA DESTA SESSÃO")
        print(
            f" P. Abrir pasta da auditoria "
            f"[{availability_badge(bool(workspace))}]"
        )
        print(
            f" I. Abrir relatório HTML   "
            f"[{availability_badge(bool(report))}]"
        )
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
    capability = provider_capabilities(
        blocks=state.runtime_blocks
    )[state.ai_provider]
    badges = menu_cost_badges(state)
    estimate = estimate_exposure(state)
    print("CONFIGURAÇÃO DA AUDITORIA\n")
    print(
        "Exposição financeira potencial: "
        + paint(
            estimate.level,
            cost_color(estimate.level),
            bold=True,
        )
    )
    if estimate.min_pages == estimate.max_pages:
        print(
            f"Volume prévio: {estimate.min_pages} página(s) conhecida(s) "
            f"× {estimate.device_contexts} contexto(s) de dispositivo"
        )
    else:
        print(
            f"Volume prévio: {estimate.min_pages} página conhecida → "
            f"teto {estimate.max_pages} × {estimate.device_contexts} "
            "contexto(s) de dispositivo"
        )
    if estimate.max_ai_attempts:
        print(
            f"IA potencial: {estimate.min_ai_attempts}–"
            f"{estimate.max_ai_attempts} tentativa(s)"
        )
    if estimate.max_web_calls:
        print(
            f"APIs M21 potenciais: {estimate.min_web_calls}–"
            f"{estimate.max_web_calls} chamada(s)"
        )
    print()
    print(
        f"1. Entrada               : "
        f"{'URL única' if state.input_mode == 'url' else 'TXT'} | "
        f"{state.target or '<não informada>'}"
    )
    print(f"2. Projeto               : {state.project or '<auto>'}")
    print(f"3. Dispositivo           : {state.device}{badges['device']}")
    print(
        f"4. IA                    : {state.ai_provider} "
        f"[{availability_badge(capability.available)}] | "
        f"{state.ai_model or '<default>'}{badges['ai']}"
    )
    print(
        f"5. Remediação textual IA : "
        f"{bool_badge(state.content_remediation)}{badges['remediation']}"
    )
    print(
        f"6. Web Performance       : {bool_badge(state.web_performance)} | "
        f"field={state.field_source}{badges['web']}"
    )
    print(f"7. max-pages             : {state.max_pages}{badges['max_pages']}")
    print(
        f"8. WebPerf max-pages     : "
        f"{state.web_max_pages}{badges['web_max_pages']}"
    )
    print(f"9. Idioma / mercado      : {state.language} / {state.market}")
    print(f"10. Raiz auditorias      : {state.audits_root}")
    ready, reason = _execution_readiness(state)
    marker = availability_badge(ready)
    reason_text = paint(reason, GREEN if ready else RED)
    print(
        f"\nH. Ajuda / custos | E. Variáveis de ambiente | "
        f"R. Executar [{marker}] {reason_text} | Q. Sair"
    )
    workspace, report = artifact_status(state)
    if workspace or report:
        print(
            f"P. Abrir última pasta [{availability_badge(bool(workspace))}] | "
            f"I. Abrir último relatório [{availability_badge(bool(report))}]"
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
                state.status, state.operation, state.error = (
                    "PRECHECK_BLOCKED",
                    "LOCAL:PRECHECK",
                    reason,
                )
                continue
            run_audit_from_console(state)
            if _post_run_actions(state):
                return 0
            state.status, state.operation, state.error = (
                "READY",
                "LOCAL:MENU",
                "",
            )
            continue
        _configure(state, choice)


if __name__ == "__main__":
    raise SystemExit(main())
