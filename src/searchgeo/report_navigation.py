"""Canonical navigation and shared presentation polish for generated reports.

All report pages use the same ordered menu. Optional pages are included only when
their HTML file exists, exactly the current page is marked active, and the final
normalization pass also applies the shared report presentation contract.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from searchgeo import __version__


NAV_ITEMS: tuple[tuple[str, str], ...] = (
    ("Visão geral", "index.html"),
    ("Relatório Mobile", "mobile.html"),
    ("Relatório Desktop", "desktop.html"),
    ("Remediações", "remediation.html"),
    ("Conteúdo e JSON-LD", "content-suggestions.html"),
    ("Acessibilidade", "accessibility.html"),
    ("Web Performance", "web-performance.html"),
    ("Uso de IA", "ai-usage.html"),
    ("Referências e metodologia", "references.html"),
)

BRASILIA_TIMEZONE = ZoneInfo("America/Sao_Paulo")

_NAV_ASIDE_RE = re.compile(
    r"<aside\b[^>]*>.*?<nav\b[^>]*>.*?</nav>.*?</aside>",
    flags=re.IGNORECASE | re.DOTALL,
)
_BR_RULE_RE = re.compile(r"\b(BR-GEO-\d{3})\b")
_TAG_SPLIT_RE = re.compile(r"(<[^>]+>)", flags=re.DOTALL)
_AI_COST_TOTAL_RE = re.compile(
    r"<section class='notice cost-total' data-api-cost-total='true'>.*?</section>",
    flags=re.DOTALL,
)
_M18_COST_RE = re.compile(
    r"<small>Custo estimado total</small><strong>([0-9]+(?:\.[0-9]+)?) USD</strong>"
)
_M20_SECTION_RE = re.compile(r"<section id='m20-ai-telemetry'.*?</section>", flags=re.DOTALL)
_M20_COST_RE = re.compile(
    r"<small>Custo estimado</small><strong>([0-9]+(?:\.[0-9]+)?) USD</strong>"
)
_PRESENTATION_MARKER = "/* searchgeo-premium-report-v1 */"

_RULE_TOOLTIPS: dict[str, str] = {
    "BR-GEO-001": "Severidade CRITICAL · Valida se o target da auditoria é válido e está normalizado.",
    "BR-GEO-002": "Severidade INFO · Exige rastreabilidade da origem de cada URL descoberta.",
    "BR-GEO-003": "Severidade LOW · Verifica aquisição e interpretação de sitemap quando disponível.",
    "BR-GEO-004": "Severidade INFO · Garante preservação dos artifacts HTTP necessários à reprodutibilidade.",
    "BR-GEO-005": "Severidade HIGH · Verifica se a página é tecnicamente recuperável.",
    "BR-GEO-006": "Severidade HIGH · Verifica se a resposta HTTP final é utilizável para o conteúdo esperado.",
    "BR-GEO-007": "Severidade HIGH · Verifica se redirects resolvem sem loop ou hop inválido.",
    "BR-GEO-008": "Severidade LOW · Detecta problemas materiais introduzidos pela cadeia de redirects.",
    "BR-GEO-009": "Severidade HIGH · Verifica se documentos HTML esperados oferecem conteúdo analisável.",
    "BR-GEO-010": "Severidade HIGH · Detecta falhas de rendering que impedem acesso a conteúdo essencial.",
    "BR-GEO-011": "Severidade HIGH · Resolve e valida diretivas de indexabilidade.",
    "BR-GEO-012": "Severidade MEDIUM · Identifica corretamente diretivas noindex explícitas.",
    "BR-GEO-013": "Severidade MEDIUM · Verifica se declarações canonical são interpretáveis e não conflitantes.",
    "BR-GEO-014": "Severidade MEDIUM · Verifica validade técnica e plausibilidade do canonical target.",
    "BR-GEO-015": "Severidade HIGH · Detecta conflitos de canonical/indexabilidade introduzidos por JavaScript.",
    "BR-GEO-016": "Severidade MEDIUM · Detecta páginas error-like que se apresentam como indexáveis.",
    "BR-GEO-017": "Severidade MEDIUM · Verifica se robots.txt é interpretável quando presente.",
    "BR-GEO-018": "Severidade HIGH · Resolve acesso separadamente para cada crawler configurado.",
    "BR-GEO-019": "Severidade HIGH · Compara RAW e RENDERED para consistência semântica material.",
    "BR-GEO-020": "Severidade HIGH · Verifica se conteúdo essencial permanece recuperável após JavaScript.",
    "BR-GEO-021": "Severidade HIGH · Verifica se rotas client-side indexáveis funcionam por acesso direto.",
    "BR-GEO-022": "Severidade MEDIUM · Verifica se navegação interna importante expõe destinos crawlable.",
    "BR-GEO-023": "Severidade HIGH · Detecta soft-404 enganoso criado por client-side routing.",
    "BR-GEO-024": "Severidade MEDIUM · Verifica se lazy loading preserva conteúdo essencial recuperável.",
    "BR-GEO-025": "Severidade HIGH · Verifica se o conteúdo principal pode ser identificado.",
    "BR-GEO-026": "Severidade HIGH · Verifica se existe conteúdo significativo além de boilerplate.",
    "BR-GEO-027": "Severidade MEDIUM · Verifica se informação essencial sobrevive à extração.",
    "BR-GEO-028": "Severidade HIGH · Verifica presença e representatividade semântica do title.",
    "BR-GEO-029": "Severidade MEDIUM · Avalia se a hierarquia semântica da página é compreensível.",
    "BR-GEO-030": "Severidade MEDIUM · Avalia se tópico principal e seções são identificáveis.",
    "BR-GEO-031": "Severidade MEDIUM · Avalia se a entidade principal é identificável quando aplicável.",
    "BR-GEO-032": "Severidade MEDIUM · Verifica contexto suficiente para tipos e relações de entidades.",
    "BR-GEO-033": "Severidade MEDIUM · Detecta ambiguidade material de entidade com evidência.",
    "BR-GEO-034": "Severidade MEDIUM · Verifica se Structured Data é sintaticamente interpretável.",
    "BR-GEO-035": "Severidade LOW · Identifica tipos e propriedades presentes em Structured Data.",
    "BR-GEO-036": "Severidade MEDIUM · Verifica consistência entre Structured Data e conteúdo visível.",
    "BR-GEO-037": "Severidade MEDIUM · Verifica consistência entre entidades estruturadas e observadas.",
    "BR-GEO-038": "Severidade HIGH · Avalia se a intenção primária da página é identificável.",
    "BR-GEO-039": "Severidade MEDIUM · Verifica se perguntas primárias relevantes recebem resposta explícita.",
    "BR-GEO-040": "Severidade MEDIUM · Verifica se respostas possuem contexto suficiente.",
    "BR-GEO-041": "Severidade LOW · Identifica claims factuais materiais quando presentes.",
    "BR-GEO-042": "Severidade MEDIUM · Verifica se claims factuais possuem contexto suficiente.",
    "BR-GEO-043": "Severidade MEDIUM · Verifica qualificadores de claims numéricos e temporais.",
    "BR-GEO-044": "Severidade MEDIUM · Detecta informação importante que exige inferência excessiva.",
    "BR-GEO-045": "Severidade MEDIUM · Verifica atribuição ou suporte para claims materiais quando requerido.",
    "BR-GEO-046": "Severidade LOW · Verifica publisher, author ou responsável quando relevante.",
    "BR-GEO-047": "Severidade MEDIUM · Verifica consistência dos sinais de publicação e freshness.",
    "BR-GEO-048": "Severidade MEDIUM · Avalia cobertura das intenções primária e secundárias.",
    "BR-GEO-049": "Severidade MEDIUM · Exige evidência para gaps materiais de intenção.",
    "BR-GEO-050": "Severidade MEDIUM · Verifica se links internos expõem destinos tecnicamente utilizáveis.",
    "BR-GEO-051": "Severidade MEDIUM · Identifica duplicatas e near-duplicates materiais no universo auditado.",
    "BR-GEO-052": "Severidade MEDIUM · Detecta e classifica diferenças materiais entre Desktop e Mobile.",
    "BR-GEO-053": "Severidade CRITICAL · Verifica rastreabilidade e reabertura de Findings, RuleExecutions e Evidences.",
    "BR-GEO-054": "Integridade do auditor · Verifica a reprodutibilidade do SCORE-GEO-001 persistido.",
}

_PREMIUM_CSS = r"""
/* searchgeo-premium-report-v1 */
:root{
  --bg:#f6f7fb;--surface:#fffefd;--ink:#273449;--muted:#6f7b8d;
  --line:rgba(111,123,141,.18);--blue:#657fc6;--green:#5f9674;
  --amber:#b68a50;--red:#bf6f70;--slate:#7d899a;--radius:16px;
  --shadow:0 10px 30px rgba(47,58,78,.055);
  --soft-blue:#eef2fb;--soft-green:#edf6f0;--soft-amber:#fbf4e8;
  --soft-red:#fbefef;--soft-slate:#f1f3f6;
}
body{background:var(--bg);color:var(--ink);font-size:14.5px;line-height:1.56}
.app-nav{background:#2f3a4d;color:#e8edf4;border-right:0;box-shadow:6px 0 24px rgba(30,41,59,.08)}
.brand{border-bottom-color:rgba(255,255,255,.12)}.brand small{color:#bac4d2}.brand strong{font-weight:650}
.app-nav a{color:#d8e0ea;font-weight:520}.app-nav a:hover,.app-nav a:focus,.app-nav a.active{background:#46536a;color:#fff}
.app-main{max-width:1440px;padding-top:34px}.app-main>*{width:min(100%,1180px);margin-left:auto;margin-right:auto}
h1{font-weight:650;letter-spacing:-.025em}h2{font-weight:630;letter-spacing:-.012em}h3,h4,h5{font-weight:620}
strong{font-weight:640}.lead,.intro,.hero>p,.panel>p,.page-card>p,.detail-body>p,.notice>p{max-width:78ch}
.panel ul,.panel ol,.detail-body ul,.detail-body ol{max-width:84ch}
.hero,.panel,.page-card,.ref-card{border-color:var(--line);border-radius:var(--radius);box-shadow:var(--shadow);background:var(--surface)}
.hero{padding:26px 28px}.panel{padding:22px 24px}.page-card{padding:18px 20px}
.metric,.score-meta div,.page-summary div,.remediation-grid>div,.confidence-explain>div{border:0;background:#f7f8fb;border-radius:11px}
.metric{padding:13px 14px}.metric small,.label,.score-meta small,.page-summary small,.remediation-grid small{color:var(--muted)}
.metric strong{font-size:.98rem;font-weight:650}.score-number{font-weight:680}.score-card{border:1px solid var(--line);border-left-width:4px;border-radius:14px;box-shadow:0 5px 18px rgba(47,58,78,.035)}
.score-card.good{background:linear-gradient(180deg,#fff 0%,var(--soft-green) 160%)}.score-card.warn{background:linear-gradient(180deg,#fff 0%,var(--soft-amber) 160%)}.score-card.bad{background:linear-gradient(180deg,#fff 0%,var(--soft-red) 150%)}
.notice{border-color:rgba(101,127,198,.22);background:var(--soft-blue);border-radius:12px}.notice.good{border-color:rgba(95,150,116,.27);background:var(--soft-green)}.notice.warn{border-color:rgba(182,138,80,.32);background:var(--soft-amber)}.notice.bad{border-color:rgba(191,111,112,.34);background:var(--soft-red)}
.badge{background:var(--soft-slate);color:#465365;font-weight:620}.badge.info{background:var(--soft-blue);color:#526ba8}.badge.good{background:var(--soft-green);color:#47785a}.badge.warn{background:var(--soft-amber);color:#8c662f}.badge.bad{background:var(--soft-red);color:#9f4f52}
.badge.bad,.badge.priority-high,.priority-high,.required{font-weight:720;box-shadow:inset 0 0 0 1px rgba(191,111,112,.28)}
.notice.bad,.score-card.bad,details:has(.badge.bad),.page-card:has(.badge.priority-high){box-shadow:0 8px 24px rgba(191,111,112,.10),inset 3px 0 0 rgba(191,111,112,.78)}
.notice.warn,.score-card.warn,.review{box-shadow:0 7px 20px rgba(182,138,80,.07)}
.table-wrap{border-color:var(--line);border-radius:12px;box-shadow:none}th{background:#f4f6f9;color:#596678;font-weight:650}th,td{border-bottom-color:rgba(111,123,141,.12)}
details{border-color:var(--line);border-radius:11px;background:#fbfbfc}summary{font-weight:620}.snapshot figure{border-color:var(--line);border-radius:12px}
pre{background:#2f394a;color:#edf1f7;border-radius:11px}.footer{max-width:78ch}
.cost-total{margin-top:-4px;margin-bottom:18px;background:linear-gradient(135deg,#eef2fb 0%,#f4f0fa 100%);border-color:rgba(101,127,198,.26);box-shadow:0 8px 24px rgba(88,104,150,.06)}
.cost-total strong{color:#40598e}.cost-total .cost-breakdown{display:block;margin-top:4px;color:var(--muted);font-size:.82rem}
.br-rule-tooltip{position:relative;display:inline-flex;align-items:center;border-bottom:1px dotted rgba(82,107,168,.6);color:#4965a4;font-weight:650;cursor:help;outline:none}
.br-rule-tooltip:focus{border-radius:4px;box-shadow:0 0 0 3px rgba(101,127,198,.16)}
.br-rule-tooltip__content{position:absolute;left:0;top:calc(100% + 8px);z-index:60;width:min(360px,78vw);padding:10px 12px;border:1px solid rgba(75,91,118,.16);border-radius:10px;background:#303b4d;color:#f5f7fb;box-shadow:0 12px 30px rgba(31,41,55,.18);font-size:.77rem;font-weight:430;line-height:1.45;opacity:0;visibility:hidden;transform:translateY(-3px);transition:opacity .12s ease,transform .12s ease,visibility .12s ease;pointer-events:none}
.br-rule-tooltip__content strong{display:block;margin-bottom:3px;color:#fff;font-size:.76rem}.br-rule-tooltip:hover .br-rule-tooltip__content,.br-rule-tooltip:focus .br-rule-tooltip__content{opacity:1;visibility:visible;transform:translateY(0)}
@media(max-width:900px){.app-main>*{width:100%}.hero{padding:21px 18px}.panel{padding:18px 16px}.page-card{padding:15px}.br-rule-tooltip__content{position:fixed;left:12px;right:12px;top:auto;bottom:16px;width:auto}}
@media print{.br-rule-tooltip{color:inherit;border:0}.br-rule-tooltip__content{display:none}.cost-total{box-shadow:none}}
"""


def available_navigation(report_dir: Path, current: str | None = None) -> tuple[tuple[str, str], ...]:
    """Return canonical menu items available in the current report projection."""
    return tuple(
        (label, filename)
        for label, filename in NAV_ITEMS
        if (report_dir / filename).is_file() or filename == current
    )


def format_report_generated_at(generated_at: datetime | None = None) -> str:
    """Return the report generation timestamp in Brasília time."""
    instant = generated_at or datetime.now(BRASILIA_TIMEZONE)
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=BRASILIA_TIMEZONE)
    else:
        instant = instant.astimezone(BRASILIA_TIMEZONE)
    return instant.strftime("%d/%m/%Y %H:%M:%S")


def render_report_navigation(
    report_dir: Path,
    current: str,
    *,
    generated_at: datetime | None = None,
    software_version: str | None = None,
) -> str:
    """Render the canonical report menu with version, timestamp and active item."""
    links = available_navigation(report_dir, current)
    rendered = "".join(
        f"<a class='{'active' if filename == current else ''}' href='{escape(filename)}'>{escape(label)}</a>"
        for label, filename in links
    )
    version = software_version or __version__
    generated_label = format_report_generated_at(generated_at)
    return (
        "<aside class='app-nav' aria-label='Navegação do relatório'>"
        "<div class='brand'>"
        "<small>SearchGEO Auditor</small>"
        "<strong>Relatório da auditoria</strong>"
        f"<small>Versão {escape(version)}</small>"
        f"<small>Gerado em {escape(generated_label)} — Horário de Brasília</small>"
        "</div>"
        f"<nav>{rendered}</nav></aside>"
    )


def normalize_report_navigation(
    report_dir: Path,
    *,
    generated_at: datetime | None = None,
    software_version: str | None = None,
) -> None:
    """Normalize menu, shared presentation, tooltips and projected API cost."""
    final_generated_at = generated_at or datetime.now(BRASILIA_TIMEZONE)
    version = software_version or __version__
    _ensure_premium_css(report_dir)
    _enhance_ai_cost_total(report_dir)
    for html_path in sorted(report_dir.glob("*.html")):
        html = html_path.read_text(encoding="utf-8")
        navigation = render_report_navigation(
            report_dir,
            html_path.name,
            generated_at=final_generated_at,
            software_version=version,
        )
        normalized, replacements = _NAV_ASIDE_RE.subn(navigation, html, count=1)
        if replacements != 1:
            raise ValueError(f"report page has no replaceable navigation: {html_path}")
        normalized = _enhance_rule_tooltips(normalized)
        html_path.write_text(normalized, encoding="utf-8", newline="\n")


def _ensure_premium_css(report_dir: Path) -> None:
    css_path = report_dir / "css" / "site.css"
    if not css_path.is_file():
        return
    css = css_path.read_text(encoding="utf-8")
    if _PRESENTATION_MARKER in css:
        return
    css_path.write_text(css.rstrip() + "\n\n" + _PREMIUM_CSS.strip() + "\n", encoding="utf-8", newline="\n")


def _enhance_ai_cost_total(report_dir: Path) -> None:
    path = report_dir / "ai-usage.html"
    if not path.is_file():
        return
    html = path.read_text(encoding="utf-8")
    html = _AI_COST_TOTAL_RE.sub("", html)
    m18_cost = _first_decimal(_M18_COST_RE, html)
    m20_cost = None
    m20_section = _M20_SECTION_RE.search(html)
    if m20_section is not None:
        m20_cost = _first_decimal(_M20_COST_RE, m20_section.group(0))
    costs = [value for value in (m18_cost, m20_cost) if value is not None]
    if not costs:
        path.write_text(html, encoding="utf-8", newline="\n")
        return
    total = sum(costs, Decimal("0"))
    breakdown = []
    if m18_cost is not None:
        breakdown.append(f"Análise M18 {_format_cost(m18_cost)} USD")
    if m20_cost is not None:
        breakdown.append(f"Remediação M20 {_format_cost(m20_cost)} USD")
    banner = (
        "<section class='notice cost-total' data-api-cost-total='true'>"
        f"<strong>Consumo projetado total de APIs com custo estimado: {_format_cost(total)} USD</strong>"
        f"<span class='cost-breakdown'>{escape(' + '.join(breakdown))}. "
        "Estimativa local; não substitui billing/invoice e não inclui integrações sem estimated_cost persistido.</span>"
        "</section>"
    )
    html = html.replace("</header>", "</header>" + banner, 1)
    path.write_text(html, encoding="utf-8", newline="\n")


def _first_decimal(pattern: re.Pattern[str], text: str) -> Decimal | None:
    match = pattern.search(text)
    if match is None:
        return None
    try:
        return Decimal(match.group(1))
    except InvalidOperation:
        return None


def _format_cost(value: Decimal) -> str:
    return f"{value:.8f}"


def _enhance_rule_tooltips(html: str) -> str:
    if "br-rule-tooltip" in html:
        return html
    parts = _TAG_SPLIT_RE.split(html)
    blocked_depth = 0
    rendered: list[str] = []
    for part in parts:
        if part.startswith("<"):
            lowered = part.lower()
            if re.match(r"<(script|style|pre|code)\b", lowered):
                blocked_depth += 1
            elif re.match(r"</(script|style|pre|code)\b", lowered):
                blocked_depth = max(0, blocked_depth - 1)
            rendered.append(part)
            continue
        if blocked_depth:
            rendered.append(part)
            continue
        rendered.append(_BR_RULE_RE.sub(_rule_tooltip_markup, part))
    return "".join(rendered)


def _rule_tooltip_markup(match: re.Match[str]) -> str:
    rule_id = match.group(1)
    detail = _RULE_TOOLTIPS.get(
        rule_id,
        "Business Rule do SearchGEO. Consulte o bloco atual para resultado, evidência e remediação aplicável.",
    )
    aria = escape(f"{rule_id}: {detail}", quote=True)
    return (
        f"<span class='br-rule-tooltip' tabindex='0' aria-label='{aria}'>"
        f"{rule_id}<span class='br-rule-tooltip__content' role='tooltip'>"
        f"<strong>{rule_id}</strong><span>{escape(detail)}</span></span></span>"
    )
