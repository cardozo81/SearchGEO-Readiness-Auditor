"""Contextual help and cost-awareness for the optional interactive console."""
from __future__ import annotations

from searchgeo.console_config import State, is_secret


COST_NONE = "SEM CUSTO EXTERNO DIRETO"
COST_EXTERNAL = "PODE GERAR CUSTO EXTERNO"
COST_EXTRA_AI = "PODE GERAR CUSTO IA ADICIONAL"
COST_QUOTA = "CONSOME API/QUOTA EXTERNA"
COST_VOLUME = "MULTIPLICADOR DE CONSUMO"


PARAMETER_HELP: tuple[tuple[str, str, str], ...] = (
    (
        "1. Entrada",
        "Define o alvo da auditoria. URL única é o padrão; TXT permite uma URL por linha, desde que todas pertençam à mesma origem normalizada.",
        COST_VOLUME + ": mais URLs úteis permitem mais páginas/contextos e, se integrações estiverem ativas, mais chamadas externas.",
    ),
    (
        "2. Projeto",
        "Nome lógico usado para identificar/organizar a auditoria. Vazio mantém o comportamento automático do SearchGEO.",
        COST_NONE,
    ),
    (
        "3. Dispositivo",
        "Escolhe mobile, desktop ou both. 'both' materializa os dois contextos quando o pipeline aplicável suporta ambos.",
        COST_VOLUME + ": 'both' pode aumentar snapshots e chamadas de IA/Web Performance por página em relação a um único dispositivo.",
    ),
    (
        "4. IA",
        "Seleciona nenhum provider, um provider explícito ou AUTO. Somente opções localmente aptas podem ser executadas.",
        COST_EXTERNAL + ": chamadas de IA podem ser cobradas pelo provider conforme modelo, tokens, plano e política comercial vigente. 'none' não faz chamada externa de IA.",
    ),
    (
        "5. Remediação textual IA",
        "Ativa o M20 para produzir sugestões textuais advisory a partir dos findings elegíveis. Não altera retroativamente score/findings.",
        COST_EXTRA_AI + ": quando ativa e há casos elegíveis, pode produzir chamadas adicionais ao provider além da análise semântica. A revisão JSON-LD determinística não depende de API externa.",
    ),
    (
        "6. Web Performance",
        "Ativa M21/Lighthouse e a fonte de field data escolhida. 'auto' pode usar PageSpeed e, quando necessário/configurado, CrUX direto.",
        COST_QUOTA + ": PageSpeed/CrUX são serviços externos. Quotas, billing e eventual cobrança pertencem ao projeto/provedor Google; o SearchGEO não transforma quota em preço monetário.",
    ),
    (
        "7. max-pages",
        "Limite máximo de páginas da auditoria principal. Também precisa comportar a quantidade de URLs únicas fornecidas em TXT.",
        COST_VOLUME + ": aumentar o limite amplia o teto de crawl, snapshots e chamadas externas potencialmente executáveis.",
    ),
    (
        "8. WebPerf max-pages",
        "Limita quantas páginas entram no enriquecimento Web Performance quando M21 está ativo.",
        COST_VOLUME + ": é o principal limitador de volume das chamadas PageSpeed/CrUX por auditoria, combinado com dispositivo e disponibilidade de dados.",
    ),
    (
        "9. Idioma / mercado",
        "Define contexto linguístico e de mercado usado pelo auditor sem mudar a URL alvo.",
        COST_NONE,
    ),
    (
        "10. Raiz auditorias",
        "Diretório onde os workspaces AUD-* são gravados. Cada auditoria mantém banco, logs e relatório dentro desse workspace.",
        COST_NONE + ": há apenas consumo local de disco.",
    ),
)


SPECIFIC_ENV_HELP: dict[str, tuple[str, str]] = {
    "SEARCHGEO_CONFIG": ("Caminho/configuração geral consumida pelo SearchGEO quando aplicável.", COST_NONE),
    "SEARCHGEO_LOG_LEVEL": ("Nível de detalhamento do log operacional.", COST_NONE),
    "SEARCHGEO_DEVICE_CONTEXT": ("Default de dispositivo: mobile, desktop ou both.", COST_VOLUME + " quando definido como both."),
    "SEARCHGEO_AI_TIMEOUT_SECONDS": ("Timeout máximo de uma tentativa de IA. Timeout não habilita retry automático.", "Não cria custo sozinho; uma chamada que chegue a ser processada pelo provider pode ser faturada conforme a política externa."),
    "SEARCHGEO_AI_CONTENT_REMEDIATION": ("Default para ativar/desativar remediação textual M20.", COST_EXTRA_AI + " quando true e houver provider/casos elegíveis."),
    "SEARCHGEO_WEB_PERFORMANCE": ("Default para ativar/desativar Web Performance M21.", COST_QUOTA + " quando true."),
    "SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES": ("Teto de páginas submetidas ao Web Performance.", COST_VOLUME),
    "SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS": ("Timeout por integração Web Performance.", "Não gera custo sozinho; controla quanto tempo a tentativa externa pode permanecer ativa."),
    "SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE": ("Fonte de field data: auto, pagespeed, crux ou none.", COST_QUOTA + " quando a fonte externa é consultada."),
    "SEARCHGEO_LIGHTHOUSE_CATEGORIES": ("Categorias Lighthouse solicitadas pelo M21.", "Pode alterar trabalho/volume da análise externa; não é preço monetário por si só."),
    "SEARCHGEO_PAGESPEED_API_KEY": ("Credencial Google para governança/autenticação da PageSpeed Insights API; pode ser opcional em uso ad hoc conforme o serviço.", COST_QUOTA + "; billing/quota pertencem ao projeto Google Cloud."),
    "SEARCHGEO_CRUX_API_KEY": ("Credencial exigida para consulta direta à Chrome UX Report API.", COST_QUOTA + "; billing/quota pertencem ao projeto Google Cloud."),
    "PLAYWRIGHT_CHROMIUM_EXECUTABLE": ("Caminho opcional para um executável Chromium local usado pela aquisição/renderização.", COST_NONE),
}


def current_cost_summary(state: State) -> tuple[str, ...]:
    """Return a conservative cost/volume summary for the current menu state."""
    lines: list[str] = []
    if state.ai_provider == "none":
        lines.append("IA externa: OFF — nenhuma chamada de IA configurada.")
    else:
        lines.append(
            f"IA externa: ON ({state.ai_provider}) — pode haver cobrança por uso conforme provider/modelo/plano."
        )
    if state.content_remediation:
        lines.append("M20 textual: ON — pode acrescentar chamadas de IA para findings elegíveis.")
    else:
        lines.append("M20 textual: OFF — sem chamadas adicionais de remediação textual.")
    if state.device == "both":
        lines.append("Dispositivo: BOTH — pode multiplicar contextos mobile/desktop e o consumo associado.")
    else:
        lines.append(f"Dispositivo: {state.device.upper()} — um único contexto de dispositivo por etapa aplicável.")
    if state.web_performance:
        lines.append(
            f"Web Performance: ON — até {state.web_max_pages} página(s), field={state.field_source}; consome API/quota externa."
        )
    else:
        lines.append("Web Performance: OFF — sem chamadas PageSpeed/CrUX pelo M21.")
    lines.append(
        f"Limite principal: max-pages={state.max_pages}. Limites maiores aumentam o teto potencial de processamento/consumo."
    )
    lines.append("Custos exibidos são alertas de exposição, não estimativa de invoice nem garantia de cobrança.")
    return tuple(lines)


def menu_cost_badges(state: State) -> dict[str, str]:
    """Short badges used by the main menu without making it visually noisy."""
    return {
        "device": " [VOLUME↑]" if state.device == "both" else "",
        "ai": " [SEM CUSTO IA]" if state.ai_provider == "none" else " [CUSTO EXTERNO]",
        "remediation": " [CUSTO IA ADICIONAL]" if state.content_remediation else "",
        "web": " [QUOTA EXTERNA]" if state.web_performance else "",
        "max_pages": " [VOLUME]",
        "web_max_pages": " [LIMITE QUOTA]" if state.web_performance else "",
    }


def environment_help(name: str) -> tuple[str, str]:
    """Describe an environment variable, with generic support for future providers."""
    if name in SPECIFIC_ENV_HELP:
        return SPECIFIC_ENV_HELP[name]
    upper = name.upper()
    if is_secret(name):
        return (
            "Credencial/token de integração externa. O console mascara o valor e usa a variável somente na sessão/processos filhos.",
            COST_EXTERNAL + ": habilitar uma credencial pode tornar chamadas externas executáveis conforme a configuração selecionada.",
        )
    if upper.endswith("_MODEL") or "_MODEL_" in upper:
        return (
            "Seleciona o modelo do provider correspondente, sujeito ao catálogo suportado pelo adapter.",
            COST_EXTERNAL + ": modelos diferentes podem ter preços diferentes no provider.",
        )
    if upper.endswith("_REASONING_EFFORT"):
        return (
            "Controla o nível de esforço de reasoning quando suportado pelo provider/modelo.",
            COST_EXTERNAL + ": maior esforço pode aumentar processamento/tokens e custo conforme o provider.",
        )
    return (
        "Variável reconhecida pelo SearchGEO. Consulte a referência de configuração para o contrato completo.",
        "Impacto financeiro não classificado automaticamente; valide a integração/serviço associado antes de habilitar em volume.",
    )


def render_help(state: State) -> None:
    print("\nAJUDA — PARÂMETROS, CONSUMO E CUSTOS")
    print("=" * 100)
    print("Legenda: custo = possível cobrança por terceiro; quota = consumo de limite externo; volume = multiplicador potencial.")
    for title, purpose, cost in PARAMETER_HELP:
        print(f"\n{title}")
        print(f"  Para que serve : {purpose}")
        print(f"  Custo/consumo  : {cost}")
    print("\nRESUMO DA CONFIGURAÇÃO ATUAL")
    for line in current_cost_summary(state):
        print("  - " + line)
    print("=" * 100)


def render_environment_help(name: str) -> None:
    purpose, cost = environment_help(name)
    print(f"\n{name}")
    print(f"  Para que serve : {purpose}")
    print(f"  Custo/consumo  : {cost}")
