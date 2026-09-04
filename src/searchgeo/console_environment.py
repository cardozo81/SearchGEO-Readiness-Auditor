"""Guided environment-variable configuration for the interactive console.

The environment surface is intentionally grouped by functional boundary instead
of exposing one flat list. Every known variable has an explicit contract:
purpose, accepted values, effective default, dependency, sensitivity and impact.
"""
from __future__ import annotations

from dataclasses import dataclass
from getpass import getpass
import os
from pathlib import Path
from urllib.parse import urlparse

from searchgeo.console_artifacts import open_external_path
from searchgeo.console_config import (
    ENV_NAMES as BASE_ENV_NAMES,
    KEY_ENV,
    PROVIDERS,
    apply_environment_defaults,
    is_secret,
)
from searchgeo.console_m23 import (
    M23_ENV_NAMES,
    apply_m23_environment_defaults,
    validate_env_value as _validate_existing,
)
from searchgeo.console_runtime import render_header
from searchgeo.console_session import mark_secret_volatile
from searchgeo.console_ui import CYAN, DIM, GREEN, paint
from searchgeo.m23_cli import (
    APDEX_CONCURRENCY_ENV,
    APDEX_DELAY_ENV,
    APDEX_ENABLED_ENV,
    APDEX_MAX_ATTEMPTS_ENV,
    APDEX_MAX_PAGES_ENV,
    APDEX_SAMPLES_ENV,
    APDEX_THRESHOLD_ENV,
    APDEX_TIMEOUT_ENV,
)
from searchgeo.provider_registry import provider_registrations
from searchgeo.provider_runtime_policy import (
    AI_TIMEOUT_ENV,
    LOWEST_REASONING,
    REASONING_OPTIONS,
    SIMPLE_DEFAULT_MODELS,
    WEB_PERFORMANCE_TIMEOUT_ENV,
    provider_reasoning_env,
)

ENV_NAMES = tuple(dict.fromkeys((*BASE_ENV_NAMES, *M23_ENV_NAMES)))
DOCUMENT_NAME = "ENVIRONMENT_VARIABLES.md"

CATEGORY_ORDER = (
    "Aplicação e execução",
    "IA — credenciais",
    "IA — modelos e reasoning",
    "IA — endpoints avançados",
    "Web Performance / Google APIs",
    "Synthetic Apdex",
    "Browser / Playwright",
)


@dataclass(frozen=True, slots=True)
class EnvironmentSpec:
    name: str
    category: str
    purpose: str
    value_type: str
    accepted: tuple[str, ...] = ()
    default: str | None = None
    required_when: str = "Nunca; override opcional."
    sensitive: bool = False
    impact: str = "Sem custo externo direto."
    example: str = ""
    source: str = "docs/ENVIRONMENT_VARIABLES.md"
    notes: str = ""


def _base_specs() -> list[EnvironmentSpec]:
    return [
        EnvironmentSpec(
            "SEARCHGEO_CONFIG", "Aplicação e execução",
            "Caminho de um arquivo TOML de configuração geral (hoje usado principalmente para logging).",
            "caminho de arquivo", default="searchgeo.toml (opcional; ausência do arquivo é válida quando a variável não está definida)",
            required_when="Somente se você quiser forçar um TOML específico; quando definida, o arquivo precisa existir.",
            example="SEARCHGEO_CONFIG=C:\\searchgeo\\searchgeo.toml",
        ),
        EnvironmentSpec(
            "SEARCHGEO_LOG_LEVEL", "Aplicação e execução",
            "Nível de verbosidade do log operacional.", "enum",
            ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"), "INFO",
            example="SEARCHGEO_LOG_LEVEL=INFO",
        ),
        EnvironmentSpec(
            "SEARCHGEO_DEVICE_CONTEXT", "Aplicação e execução",
            "Default de dispositivo quando a CLI/menu não fornece valor explícito.", "enum",
            ("mobile", "desktop", "both"), "mobile",
            impact="`both` multiplica contextos e pode aumentar chamadas externas, tempo e custo.",
            example="SEARCHGEO_DEVICE_CONTEXT=mobile",
        ),
        EnvironmentSpec(
            AI_TIMEOUT_ENV, "Aplicação e execução",
            "Timeout máximo de cada tentativa de IA; não é o timeout da auditoria inteira.", "número > 0 (segundos)",
            default="180", impact="Não cria chamadas; uma chamada que expirou localmente ainda pode ter sido processada/faturada pelo provider.",
            example=f"{AI_TIMEOUT_ENV}=180",
        ),
        EnvironmentSpec(
            "SEARCHGEO_AI_CONTENT_REMEDIATION", "Aplicação e execução",
            "Default da remediação textual por IA.", "booleano", ("true", "false"), "false",
            required_when="Nunca. Só tem efeito com provider de IA apto.",
            impact="Quando true, pode criar chamadas adicionais de IA e custo adicional.",
            example="SEARCHGEO_AI_CONTENT_REMEDIATION=false",
        ),
        EnvironmentSpec(
            "SEARCHGEO_WEB_PERFORMANCE", "Web Performance / Google APIs",
            "Default para habilitar coleta PageSpeed/Lighthouse/CrUX.", "booleano", ("true", "false"), "false",
            impact="Quando true, consome integrações/quota externa.",
            example="SEARCHGEO_WEB_PERFORMANCE=false",
        ),
        EnvironmentSpec(
            "SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES", "Web Performance / Google APIs",
            "Limita quantas páginas auditadas são submetidas às integrações de Web Performance; 0 significa todas.",
            "inteiro >= 0", default="10", impact="Multiplicador direto do volume potencial de PageSpeed/CrUX.",
            example="SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES=10",
        ),
        EnvironmentSpec(
            WEB_PERFORMANCE_TIMEOUT_ENV, "Web Performance / Google APIs",
            "Tempo máximo de espera por chamada externa PageSpeed/CrUX.", "número > 0 (segundos)",
            default="120", impact="Não cria chamadas; controla apenas quanto o cliente espera.",
            example=f"{WEB_PERFORMANCE_TIMEOUT_ENV}=120",
        ),
        EnvironmentSpec(
            "SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE", "Web Performance / Google APIs",
            "Define a política de dados de campo (CrUX) usada pelo Web Performance.", "enum",
            ("auto", "pagespeed", "crux", "none"), "auto",
            required_when="`crux` exige SEARCHGEO_CRUX_API_KEY; os demais valores não exigem essa chave direta.",
            impact="Pode consumir PageSpeed e/ou CrUX conforme a opção.",
            example="SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE=auto",
        ),
        EnvironmentSpec(
            "SEARCHGEO_LIGHTHOUSE_CATEGORIES", "Web Performance / Google APIs",
            "Categorias Lighthouse solicitadas numa chamada PageSpeed.", "lista CSV",
            ("performance", "accessibility", "best-practices", "seo"),
            "performance,accessibility,best-practices,seo",
            impact="Altera as categorias coletadas; não representa preço monetário por si só.",
            example="SEARCHGEO_LIGHTHOUSE_CATEGORIES=performance,accessibility,best-practices,seo",
            notes="Use uma ou mais categorias suportadas, separadas por vírgula, sem duplicar.",
        ),
        EnvironmentSpec(
            "SEARCHGEO_PAGESPEED_API_KEY", "Web Performance / Google APIs",
            "Chave Google usada pela PageSpeed Insights API.", "segredo/API key",
            required_when="Recomendada quando Web Performance estiver habilitado e quota autenticada for necessária.",
            sensitive=True, impact="Habilita consumo de API/quota do projeto Google Cloud; billing depende da conta/projeto.",
            example="SEARCHGEO_PAGESPEED_API_KEY=<sua-chave>",
            source="docs/GOOGLE_API_KEYS.md — Google Cloud Console / PageSpeed Insights API",
        ),
        EnvironmentSpec(
            "SEARCHGEO_CRUX_API_KEY", "Web Performance / Google APIs",
            "Chave Google usada para consulta direta à Chrome UX Report API.", "segredo/API key",
            required_when="Obrigatória quando field source = crux; útil como fallback direto em auto.",
            sensitive=True, impact="Habilita consumo de API/quota do projeto Google Cloud; billing depende da conta/projeto.",
            example="SEARCHGEO_CRUX_API_KEY=<sua-chave>",
            source="docs/GOOGLE_API_KEYS.md — Google Cloud Console / Chrome UX Report API",
        ),
        EnvironmentSpec(
            "PLAYWRIGHT_CHROMIUM_EXECUTABLE", "Browser / Playwright",
            "Caminho opcional para um executável Chromium existente; substitui a descoberta padrão do browser Playwright.",
            "caminho de arquivo", required_when="Somente quando quiser usar um Chromium específico.",
            example="PLAYWRIGHT_CHROMIUM_EXECUTABLE=C:\\Program Files\\Chromium\\chrome.exe",
        ),
    ]


_KEY_SOURCES = {
    "OPENAI": "OpenAI Platform > projeto > API Keys — https://platform.openai.com/api-keys",
    "DEEPSEEK": "DeepSeek Platform > API Keys — https://platform.deepseek.com/api_keys",
    "MIMO": "Xiaomi MiMo Open Platform > Console > API Keys — https://mimo.mi.com/docs/en-US/quick-start/faq/api-integration",
    "XAI": "xAI Console > API Keys — https://console.x.ai/",
    "QWEN": "Alibaba Cloud Model Studio > API Key — https://www.alibabacloud.com/help/en/model-studio/first-api-call-to-qwen",
    "GEMINI": "Google AI Studio > API Keys — https://aistudio.google.com/apikey",
    "ANTHROPIC": "Anthropic Console > API Keys — https://console.anthropic.com/",
}

_ENDPOINT_DEFAULTS = {
    "XAI": "https://api.x.ai/v1/responses",
    "QWEN": "https://dashscope-us.aliyuncs.com/compatible-mode/v1/chat/completions",
    "GEMINI": "https://generativelanguage.googleapis.com/v1beta/interactions",
    "ANTHROPIC": "https://api.anthropic.com/v1/messages",
}


def _provider_specs() -> list[EnvironmentSpec]:
    specs: list[EnvironmentSpec] = []
    for registration in provider_registrations():
        provider = registration.provider_name
        prefix_note = (
            " O adapter atual aceita somente chave PAYG `sk-...`; Token Plan `tp-...` usa endpoint/produto diferente."
            if provider == "MIMO" else ""
        )
        specs.append(EnvironmentSpec(
            registration.key_env, "IA — credenciais",
            f"Credencial do provider {registration.display_name}.{prefix_note}", "segredo/API key",
            required_when=f"Obrigatória quando o provider `{registration.id}` é selecionado; em AUTO é necessária para tornar esse provider elegível.",
            sensitive=True, impact="Pode tornar chamadas externas de IA executáveis e gerar cobrança conforme modelo/plano.",
            example=f"{registration.key_env}=<sua-chave>", source=_KEY_SOURCES[provider],
        ))
        specs.append(EnvironmentSpec(
            registration.model_env, "IA — modelos e reasoning",
            f"Modelo usado por {registration.display_name} quando não houver --ai-model explícito.", "enum",
            tuple(registration.supported_models), SIMPLE_DEFAULT_MODELS[provider],
            required_when="Nunca; use apenas para sobrescrever o modelo público default.",
            impact="Modelos podem ter preços, latência e capacidade diferentes.",
            example=f"{registration.model_env}={SIMPLE_DEFAULT_MODELS[provider]}",
        ))
        reasoning_env = provider_reasoning_env(provider)
        if reasoning_env:
            specs.append(EnvironmentSpec(
                reasoning_env, "IA — modelos e reasoning",
                f"Esforço/profundidade de reasoning para {registration.display_name}.", "enum",
                tuple(REASONING_OPTIONS[provider]), LOWEST_REASONING[provider],
                required_when="Nunca; o menor nível efetivamente suportado é aplicado quando não há override.",
                impact="Esforço maior pode aumentar latência, tokens e custo conforme o provider/modelo.",
                example=f"{reasoning_env}={LOWEST_REASONING[provider]}",
            ))
        if registration.endpoint_env:
            specs.append(EnvironmentSpec(
                registration.endpoint_env, "IA — endpoints avançados",
                f"Override avançado do endpoint HTTP usado por {registration.display_name}.", "URL absoluta HTTP(S)",
                default=_ENDPOINT_DEFAULTS.get(provider),
                required_when="Nunca no uso normal; altere somente para endpoint oficialmente compatível/proxy controlado.",
                impact="Endpoint incorreto pode causar falha, cobrança em serviço diferente ou envio de dados a destino indevido.",
                example=f"{registration.endpoint_env}={_ENDPOINT_DEFAULTS.get(provider, '<url>')}",
                notes="Não altere sem necessidade operacional comprovada.",
            ))
    return specs


def _apdex_specs() -> list[EnvironmentSpec]:
    return [
        EnvironmentSpec(APDEX_ENABLED_ENV, "Synthetic Apdex", "Habilita navegações sintéticas repetidas em Chromium.", "booleano", ("true", "false"), "false", impact="Não usa API paga própria, mas gera carga HTTP real contra o alvo.", example=f"{APDEX_ENABLED_ENV}=false"),
        EnvironmentSpec(APDEX_THRESHOLD_ENV, "Synthetic Apdex", "Threshold T em segundos: <=T Satisfied; >T até 4T Tolerating; >4T Frustrated.", "número > 0 (segundos)", required_when="Obrigatória quando Synthetic Apdex=true.", impact="Define a classificação Apdex; não cria custo financeiro externo.", example=f"{APDEX_THRESHOLD_ENV}=1.5"),
        EnvironmentSpec(APDEX_SAMPLES_ENV, "Synthetic Apdex", "Quantidade alvo de amostras válidas por URL/dispositivo.", "inteiro >= 1", default="100", impact="Multiplica diretamente o número de navegações; 1–99 é small-group diagnóstico.", example=f"{APDEX_SAMPLES_ENV}=100"),
        EnvironmentSpec(APDEX_MAX_ATTEMPTS_ENV, "Synthetic Apdex", "Teto de tentativas para repor amostras inválidas.", "inteiro >= amostras válidas", default="ceil(1.25 × samples)", impact="Aumenta o teto de carga real no alvo.", example=f"{APDEX_MAX_ATTEMPTS_ENV}=125"),
        EnvironmentSpec(APDEX_MAX_PAGES_ENV, "Synthetic Apdex", "Máximo de páginas medidas; 0 significa todas as páginas disponíveis.", "inteiro >= 0", default="1", impact="Multiplica a quantidade total de contextos/navegações.", example=f"{APDEX_MAX_PAGES_ENV}=1"),
        EnvironmentSpec(APDEX_TIMEOUT_ENV, "Synthetic Apdex", "Timeout de cada navegação sintética.", "número > 0 e > 4T", default="max(45, 4T + 5) quando habilitado", required_when="Se definido explicitamente com Apdex ativo, precisa ser >4T.", impact="Timeout muito baixo invalida a classificação Frustrated.", example=f"{APDEX_TIMEOUT_ENV}=45"),
        EnvironmentSpec(APDEX_DELAY_ENV, "Synthetic Apdex", "Intervalo mínimo entre inícios de navegações.", "número >= 0 (segundos)", default="1", impact="Valor maior reduz pressão no site e aumenta duração total.", example=f"{APDEX_DELAY_ENV}=1"),
        EnvironmentSpec(APDEX_CONCURRENCY_ENV, "Synthetic Apdex", "Quantidade de workers sintéticos simultâneos.", "enum inteiro", ("1", "2"), "1", impact="2 reduz tempo, mas aumenta carga concorrente contra o alvo.", example=f"{APDEX_CONCURRENCY_ENV}=1"),
    ]


def environment_specs() -> tuple[EnvironmentSpec, ...]:
    by_name: dict[str, EnvironmentSpec] = {}
    for spec in (*_base_specs(), *_provider_specs(), *_apdex_specs()):
        by_name[spec.name] = spec
    result: list[EnvironmentSpec] = []
    for name in ENV_NAMES:
        result.append(by_name.get(name, EnvironmentSpec(
            name, "Aplicação e execução", "Variável reconhecida pelo SearchGEO.", "texto",
            required_when="Consulte a documentação antes de definir.",
            sensitive=is_secret(name), impact="Impacto não classificado; valide antes de usar.",
        )))
    return tuple(result)


_SPECS = environment_specs()
_SPEC_BY_NAME = {spec.name: spec for spec in _SPECS}


def _status(state: object, spec: EnvironmentSpec) -> str:
    value = (os.environ.get(spec.name) or "").strip()
    if value:
        if spec.sensitive or is_secret(spec.name):
            return paint("[SET]", GREEN, bold=True)
        if value.casefold() in {"true", "1", "yes", "on"}:
            return paint(value, GREEN, bold=True)
        if value.casefold() in {"false", "0", "no", "off"}:
            return paint(value, DIM)
        return paint(value[:60], CYAN)
    if spec.default is not None:
        return paint(f"<default efetivo: {spec.default}>", DIM)
    return paint("<não definida>", DIM)


def _documentation_path() -> Path | None:
    candidates = (
        Path.cwd() / "docs" / DOCUMENT_NAME,
        Path(__file__).resolve().parents[2] / "docs" / DOCUMENT_NAME,
    )
    for path in candidates:
        if path.is_file():
            return path
    return None


def _open_documentation(state: object) -> None:
    path = _documentation_path()
    if path is None:
        setattr(state, "error", f"documentação não encontrada: docs/{DOCUMENT_NAME}")
        return
    ok, detail = open_external_path(path)
    setattr(state, "operation", "LOCAL:OPEN_ENV_DOCUMENTATION")
    setattr(state, "error", "" if ok else detail)


def _validate_value(name: str, raw: str) -> str:
    value = _validate_existing(name, raw)
    if name == "SEARCHGEO_LOG_LEVEL":
        normalized = value.upper()
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        if normalized not in allowed:
            raise ValueError("use CRITICAL, ERROR, WARNING, INFO ou DEBUG")
        return normalized
    if name == "SEARCHGEO_CONFIG":
        path = Path(value).expanduser()
        if not path.is_file():
            raise ValueError("arquivo TOML configurado não existe")
        return str(path)
    if name == "SEARCHGEO_LIGHTHOUSE_CATEGORIES":
        allowed = ("performance", "accessibility", "best-practices", "seo")
        items = [item.strip().casefold() for item in value.split(",") if item.strip()]
        if not items:
            raise ValueError("informe ao menos uma categoria Lighthouse")
        invalid = [item for item in items if item not in allowed]
        if invalid:
            raise ValueError("categorias suportadas: " + ", ".join(allowed))
        if len(items) != len(set(items)):
            raise ValueError("não duplique categorias Lighthouse")
        return ",".join(items)
    spec = _SPEC_BY_NAME.get(name)
    if spec and spec.category == "IA — endpoints avançados":
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("use URL absoluta http:// ou https://")
    return value


def _after_environment_change(state: object, name: str) -> None:
    issues = list(apply_environment_defaults(state, names={name}))
    issues.extend(apply_m23_environment_defaults(state, names={name}))
    setattr(state, "error", "; ".join(issues))
    for selection, provider in PROVIDERS.items():
        if KEY_ENV[provider] == name:
            getattr(state, "runtime_blocks", {}).pop(selection, None)


def _prompt_enum(spec: EnvironmentSpec) -> str | None:
    print("\nValores aceitos:")
    for index, item in enumerate(spec.accepted, 1):
        default = " [default]" if spec.default == item else ""
        print(f" {index}. {item}{default}")
    print(" 0. cancelar")
    raw = input("Escolha: ").strip()
    if raw == "0":
        return None
    try:
        return spec.accepted[int(raw) - 1]
    except (ValueError, IndexError):
        if raw in spec.accepted:
            return raw
        raise ValueError("opção inválida")


def _set_variable(state: object, spec: EnvironmentSpec) -> None:
    render_header(state)
    _render_detail(state, spec, include_actions=False)
    try:
        if spec.accepted and spec.value_type in {"enum", "enum inteiro"}:
            raw = _prompt_enum(spec)
            if raw is None:
                return
        else:
            prompt = f"Novo valor para {spec.name}: "
            raw = getpass(prompt) if spec.sensitive or is_secret(spec.name) else input(prompt)
        os.environ[spec.name] = _validate_value(spec.name, raw)
        if spec.sensitive or is_secret(spec.name):
            mark_secret_volatile(state)
        _after_environment_change(state, spec.name)
    except (ValueError, OverflowError) as exc:
        setattr(state, "error", str(exc))


def _remove_variable(state: object, spec: EnvironmentSpec) -> None:
    os.environ.pop(spec.name, None)
    if spec.sensitive or is_secret(spec.name):
        mark_secret_volatile(state)
    _after_environment_change(state, spec.name)


def _render_detail(state: object, spec: EnvironmentSpec, *, include_actions: bool = True) -> None:
    print(spec.name)
    print("=" * min(max(len(spec.name), 40), 100))
    print(f"Grupo          : {spec.category}")
    print(f"Para que serve : {spec.purpose}")
    print(f"Tipo           : {spec.value_type}")
    if spec.accepted:
        print(f"Valores aceitos: {', '.join(spec.accepted)}")
    print(f"Default efetivo: {spec.default if spec.default is not None else 'nenhum'}")
    print(f"Obrigatória    : {spec.required_when}")
    print(f"Sensível       : {'SIM — nunca exibida/gravada no INI' if spec.sensitive or is_secret(spec.name) else 'não'}")
    print(f"Custo/impacto  : {spec.impact}")
    print(f"Valor ambiente : {_status(state, spec)}")
    if spec.example:
        print(f"Exemplo        : {spec.example}")
    if spec.source:
        print(f"Como obter/ref.: {spec.source}")
    if spec.notes:
        print(f"Observação     : {spec.notes}")
    if spec.default is not None and not (os.environ.get(spec.name) or "").strip():
        print(paint("Nota: não é necessário gravar a variável para usar o default; o SearchGEO já aplica o valor internamente.", DIM))
    if include_actions:
        print("\nS. Setar/alterar | R. Remover override | D. Abrir documentação detalhada | V. Voltar")


def _variable_menu(state: object, spec: EnvironmentSpec) -> None:
    while True:
        render_header(state)
        _render_detail(state, spec)
        action = input("Escolha: ").strip().upper()
        if action == "V":
            return
        if action == "D":
            _open_documentation(state)
            continue
        if action == "S":
            _set_variable(state, spec)
            continue
        if action == "R":
            _remove_variable(state, spec)


def _category_menu(state: object, category: str, specs: tuple[EnvironmentSpec, ...]) -> None:
    while True:
        render_header(state)
        print(f"VARIÁVEIS DE AMBIENTE — {category}\n")
        for index, spec in enumerate(specs, 1):
            print(f"{index:2d}. {spec.name:<44} {_status(state, spec)}")
        print("\nD. Abrir documentação detalhada | V. Voltar")
        raw = input("Selecione a variável: ").strip().upper()
        if raw == "V":
            return
        if raw == "D":
            _open_documentation(state)
            continue
        try:
            _variable_menu(state, specs[int(raw) - 1])
        except (ValueError, IndexError):
            setattr(state, "error", "variável inválida")


def environment_menu(state: object) -> None:
    """Render grouped, guided environment configuration with one logical screen at a time."""
    by_category = {
        category: tuple(spec for spec in _SPECS if spec.category == category)
        for category in CATEGORY_ORDER
    }
    while True:
        render_header(state)
        print("CONFIGURAÇÃO AVANÇADA — VARIÁVEIS DE AMBIENTE\n")
        print("Os defaults seguros já são aplicados internamente. Defina variável somente para override ou credencial.")
        print("Secrets aparecem apenas como [SET] e nunca são gravados no INI.\n")
        choices: dict[str, str] = {}
        for index, category in enumerate(CATEGORY_ORDER, 1):
            specs = by_category[category]
            configured = sum(1 for spec in specs if (os.environ.get(spec.name) or "").strip())
            print(f" {index}. {category:<31} {configured}/{len(specs)} override(s) definidos")
            choices[str(index)] = category
        print("\n A. Todas as variáveis")
        print(f" D. Abrir documentação detalhada (docs/{DOCUMENT_NAME})")
        print(" V. Voltar")
        raw = input("Escolha: ").strip().upper()
        if raw == "V":
            return
        if raw == "D":
            _open_documentation(state)
            continue
        if raw == "A":
            _category_menu(state, "Todas", _SPECS)
            continue
        category = choices.get(raw)
        if category:
            _category_menu(state, category, by_category[category])
        else:
            setattr(state, "error", "grupo inválido")
