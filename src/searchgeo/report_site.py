"""Static multi-page HTML report site assembled from persisted audit data.

This module is intentionally projection-only. It never recalculates findings or
scores and it never calls an external AI provider. The SQLite workspace remains
source of truth.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from html import escape
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

from searchgeo.actionability import Actionability, classify_actionability, label_for
from searchgeo.persistence import AuditWorkspace
from searchgeo.reporting import _score_classification
from searchgeo.rule_references import references_for, VERIFIED_ON

REPORT_DIR = "report"
INDEX_FILE = "index.html"
MOBILE_FILE = "mobile.html"
DESKTOP_FILE = "desktop.html"
REMEDIATION_FILE = "remediation.html"
AI_FILE = "ai-usage.html"
REFERENCES_FILE = "references.html"
CSS_FILE = "css/site.css"

_DIMENSION_LABELS = {
    "TECHNICAL_ACCESSIBILITY": "Acessibilidade técnica",
    "INDEXABILITY": "Capacidade de indexação",
    "CONTENT_EXTRACTABILITY": "Extração de conteúdo",
    "SEMANTIC_STRUCTURE": "Estrutura semântica",
    "ENTITY_CLARITY": "Clareza de entidades",
    "STRUCTURED_DATA": "Dados estruturados",
    "ANSWERABILITY": "Capacidade de resposta",
    "CITATION_READINESS": "Preparação para citação",
    "EVIDENCE_TRUST": "Evidências e confiabilidade",
    "INTENT_COVERAGE": "Cobertura de intenções",
    "OVERALL_READINESS": "Readiness GEO",
}

_STATUS_LABELS = {
    "PASS": "Aprovado",
    "FAIL": "Problema",
    "WARNING": "Alerta",
    "UNKNOWN": "Não determinado",
    "NOT_APPLICABLE": "Não aplicável",
    "ERROR": "Erro de análise",
    "CONSOLIDATED": "Consolidado",
    "PARTIAL": "Parcial",
    "NOT_CONSOLIDATED": "Não consolidado",
    "HIGH": "Alta",
    "MEDIUM": "Média",
    "LOW": "Baixa",
    "UNAVAILABLE": "Indisponível",
}

_SITE_CSS = r"""
:root{
  --nav:248px;--bg:#f5f7fa;--surface:#fff;--ink:#172033;--muted:#657084;
  --line:#e3e8ef;--blue:#2457d6;--green:#19733b;--amber:#a76800;--orange:#b24b00;
  --red:#b42318;--slate:#667085;--radius:14px;--shadow:0 1px 3px rgba(16,24,40,.06)
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;font-size:15px;line-height:1.48}
a{color:var(--blue)}
img{max-width:100%;height:auto}
.app-nav{position:fixed;inset:0 auto 0 0;width:var(--nav);padding:22px 14px;background:#111827;color:#dbe4f0;border-right:1px solid #273244;overflow-y:auto;z-index:20}
.brand{padding:0 9px 16px;border-bottom:1px solid #273244;margin-bottom:14px}
.brand small{display:block;color:#93a4ba;font-size:.69rem;text-transform:uppercase;letter-spacing:.12em}
.brand strong{display:block;margin-top:4px;color:#fff;font-size:.98rem}
.app-nav nav{display:grid;gap:5px}
.app-nav a{display:block;padding:9px 10px;border-radius:8px;color:#cbd5e1;text-decoration:none;font-size:.84rem}
.app-nav a:hover,.app-nav a:focus,.app-nav a.active{background:#243044;color:#fff;outline:none}
.app-main{margin-left:var(--nav);padding:30px 34px 60px;max-width:1500px;min-width:0}
.hero,.panel,.card,.page-card,.notice,.metric,.table-wrap,.score-card,.ref-card{min-width:0}
.hero{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:24px 26px;box-shadow:var(--shadow);margin-bottom:18px}
.eyebrow{font-size:.71rem;text-transform:uppercase;letter-spacing:.11em;color:var(--muted);font-weight:700}
h1{font-size:clamp(1.75rem,2.4vw,2.35rem);line-height:1.12;margin:.3rem 0 .65rem}
h2{font-size:clamp(1.15rem,1.7vw,1.45rem);line-height:1.25;margin:0 0 .8rem}
h3{font-size:1rem;line-height:1.3;margin:.2rem 0 .55rem}
h4,h5{font-size:.92rem;margin:1rem 0 .45rem}
p{margin:.55rem 0}
.lead,.intro{max-width:82ch;color:#4b5565}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.metric-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-top:18px}
.metric{border:1px solid var(--line);background:#fbfcfe;border-radius:10px;padding:12px}
.metric small,.label{display:block;color:var(--muted);font-size:.73rem}
.metric strong{display:block;margin-top:3px;font-size:1rem;overflow-wrap:anywhere}
.score-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin-top:18px}
.score-card{background:#fff;border:1px solid var(--line);border-left:5px solid var(--slate);border-radius:12px;padding:16px}
.score-card.good{border-left-color:var(--green)}.score-card.warn{border-left-color:var(--amber)}.score-card.bad{border-left-color:var(--red)}
.score-number{font-size:clamp(1.8rem,3vw,2.4rem);font-weight:700;line-height:1;margin:.25rem 0 .4rem}
.score-number span{font-size:.82rem;color:var(--muted);font-weight:500}
.score-meta{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:12px}
.score-meta div{background:#f8fafc;border-radius:8px;padding:8px;min-width:0}
.score-meta small{display:block;color:var(--muted);font-size:.7rem}
.score-meta strong{font-size:.83rem;overflow-wrap:anywhere}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px;box-shadow:var(--shadow);margin:14px 0}
.panel-head{display:flex;gap:12px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap}
.kicker{font-size:.69rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);font-weight:700;margin-bottom:4px}
.notice{border:1px solid #c9d7f5;background:#f0f5ff;border-radius:10px;padding:12px 14px;margin:12px 0}
.notice.warn{border-color:#f0d29f;background:#fff8eb}.notice.bad{border-color:#f0b5b0;background:#fff1f0}
.notice strong{font-weight:700}
.badge{display:inline-flex;align-items:center;border-radius:999px;padding:4px 8px;font-size:.7rem;font-weight:700;background:#edf1f5;color:#344054;white-space:nowrap}
.badge.good{background:#eaf7ee;color:var(--green)}.badge.warn{background:#fff3d8;color:#855100}.badge.bad{background:#feeceb;color:var(--red)}.badge.info{background:#eaf1ff;color:#244ea4}
.badge.unknown{background:#eef0f3;color:#596274}
.table-wrap{width:100%;max-width:100%;overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:#fff}
table{width:100%;border-collapse:collapse;font-size:.84rem}
th,td{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid #edf0f4}
th{background:#f8fafc;color:#4b5565;font-size:.73rem;text-transform:uppercase;letter-spacing:.03em}
tr:last-child td{border-bottom:0}
.mono,code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.mono{overflow-wrap:anywhere}
pre{margin:.6rem 0;max-width:100%;overflow-x:auto;white-space:pre-wrap;overflow-wrap:anywhere;background:#111827;color:#e5e7eb;border-radius:9px;padding:11px;font-size:.78rem}
.page-card{background:#fff;border:1px solid var(--line);border-radius:12px;margin:12px 0;padding:16px}
.page-url{font-size:.9rem;overflow-wrap:anywhere}
.page-summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:10px 0}
.page-summary div{background:#f8fafc;border-radius:8px;padding:9px;min-width:0}
.page-summary small{display:block;color:var(--muted);font-size:.69rem}.page-summary strong{font-size:.82rem;overflow-wrap:anywhere}
.snapshot{display:grid;grid-template-columns:minmax(180px,310px) minmax(0,1fr);gap:14px;align-items:start;margin-top:12px}
.snapshot figure{margin:0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fff}
.snapshot figcaption{padding:7px 9px;font-size:.72rem;color:var(--muted)}
.finding{border-top:1px solid var(--line);padding:11px 0}.finding:first-child{border-top:0}
.finding-head{display:flex;align-items:center;gap:7px;justify-content:space-between;flex-wrap:wrap}
.finding-title{font-size:.91rem;font-weight:650}
details{border:1px solid var(--line);border-radius:9px;background:#fbfcfd;margin:8px 0}
summary{cursor:pointer;padding:9px 11px;font-weight:650;font-size:.84rem}
details>div,details>p,details>pre,details>table,details>ul,details>ol{margin-left:11px;margin-right:11px}
.ref-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}
.ref-card{border:1px solid var(--line);border-radius:10px;padding:13px;background:#fff}
.ref-card a{overflow-wrap:anywhere}
.footer{margin-top:24px;color:var(--muted);font-size:.76rem}
.confidence-explain{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:12px}
.confidence-explain>div{border:1px solid var(--line);border-radius:10px;padding:12px;background:#fbfcfe}
.confidence-explain strong{display:block;margin-bottom:4px;font-size:.88rem}
.confidence-explain p{font-size:.82rem;color:#526071}
@media(max-width:900px){
  .app-nav{position:sticky;top:0;width:auto;height:auto;inset:auto;padding:9px 10px;overflow-x:auto}
  .brand{display:none}.app-nav nav{display:flex;min-width:max-content;gap:5px}.app-nav a{background:#243044}
  .app-main{margin-left:0;padding:18px 12px 42px}.snapshot{grid-template-columns:1fr}
  .score-meta,.confidence-explain{grid-template-columns:1fr}
}
@media print{
  body{background:#fff}.app-nav{display:none}.app-main{margin:0;max-width:none;padding:0}
  .hero,.panel,.page-card{box-shadow:none;break-inside:avoid}
}
"""

_OFFICIAL_REFERENCE_CATALOG = (
    ("Google Search Central", "Search Essentials", "https://developers.google.com/search/docs/essentials",
     "Requisitos e práticas fundamentais de rastreamento, indexação, spam e conteúdo útil."),
    ("Google Search Central", "SEO Starter Guide", "https://developers.google.com/search/docs/fundamentals/seo-starter-guide",
     "Fundamentos de descoberta, organização, conteúdo e interpretação por mecanismos de busca."),
    ("Google Search Central", "Structured data", "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data",
     "Princípios de dados estruturados e coerência entre marcação e conteúdo visível."),
    ("Google Search Central", "Canonicalization", "https://developers.google.com/search/docs/crawling-indexing/canonicalization",
     "Sinais de canonicalização e escolha de URL representativa."),
    ("Google Crawling Infrastructure", "robots.txt", "https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec",
     "Interpretação do protocolo robots.txt pelo Google."),
    ("OpenAI", "Publishers and Developers — FAQ", "https://help.openai.com/en/articles/12627856-publishers-and-developers-faq",
     "Controles de acesso para OAI-SearchBot e GPTBot."),
    ("Schema.org", "Schema.org documentation", "https://schema.org/docs/documents.html",
     "Vocabulário comunitário usado para descrever entidades e propriedades estruturadas."),
    ("WHATWG", "HTML Living Standard — Sections", "https://html.spec.whatwg.org/dev/sections.html",
     "Semântica estrutural de seções e headings em HTML."),
    ("IETF / RFC Editor", "RFC 9309 — Robots Exclusion Protocol", "https://www.rfc-editor.org/rfc/rfc9309.html",
     "Especificação formal do Robots Exclusion Protocol."),
    ("IETF / RFC Editor", "RFC 9110 — HTTP Semantics", "https://www.rfc-editor.org/rfc/rfc9110.html",
     "Semântica normativa de HTTP, incluindo status e comportamento de respostas."),
)


def materialize_report_site(*, audit_id: str, workspace: AuditWorkspace) -> Path:
    """Create the navigable static report site and return report/index.html."""

    report_dir = workspace.root / REPORT_DIR
    css_dir = report_dir / "css"
    css_dir.mkdir(parents=True, exist_ok=True)

    data = _load(audit_id, workspace)
    available_devices = _available_devices(data)
    nav = _navigation(available_devices)

    (css_dir / "site.css").write_text(_SITE_CSS.strip() + "\n", encoding="utf-8")
    (report_dir / INDEX_FILE).write_text(
        _shell("Visão geral", INDEX_FILE, nav, _overview(data, available_devices)),
        encoding="utf-8",
    )
    for device, filename in (("MOBILE", MOBILE_FILE), ("DESKTOP", DESKTOP_FILE)):
        if device in available_devices:
            (report_dir / filename).write_text(
                _shell(_device_label(device), filename, nav, _device_page(data, device)),
                encoding="utf-8",
            )
    (report_dir / REMEDIATION_FILE).write_text(
        _shell("Remediações", REMEDIATION_FILE, nav, _remediation_page(data)),
        encoding="utf-8",
    )
    (report_dir / AI_FILE).write_text(
        _shell("Uso de IA", AI_FILE, nav, _ai_page(data)),
        encoding="utf-8",
    )
    (report_dir / REFERENCES_FILE).write_text(
        _shell("Referências e metodologia", REFERENCES_FILE, nav, _references_page()),
        encoding="utf-8",
    )

    for legacy_name in ("report.html", "remediation.html"):
        legacy = workspace.root / legacy_name
        if legacy.exists():
            legacy.unlink()

    return report_dir / INDEX_FILE


def _load(audit_id: str, workspace: AuditWorkspace) -> dict[str, Any]:
    connection = sqlite3.connect(workspace.database)
    connection.row_factory = sqlite3.Row
    try:
        audit = connection.execute("SELECT * FROM audits WHERE audit_id=?", (audit_id,)).fetchone()
        if audit is None:
            raise ValueError(f"audit not found: {audit_id}")
        pages = list(connection.execute(
            "SELECT * FROM pages WHERE audit_id=? ORDER BY depth,normalized_url", (audit_id,)
        ).fetchall())
        snapshots = _optional(connection, """
            SELECT ps.*,p.normalized_url FROM page_snapshots ps
            JOIN pages p ON p.page_id=ps.page_id
            WHERE p.audit_id=? ORDER BY p.normalized_url,ps.device
        """, (audit_id,))
        scores = _optional(connection, "SELECT * FROM scores WHERE audit_id=? ORDER BY device,dimension", (audit_id,))
        findings = _optional(connection, """
            SELECT f.*,re.result AS rule_result,re.observed_value AS execution_observed_value
            FROM findings f JOIN rule_executions re ON re.rule_execution_id=f.rule_execution_id
            WHERE f.audit_id=? ORDER BY f.rule_id,f.page_id,f.device,f.finding_id
        """, (audit_id,))
        groups = _optional(connection, "SELECT * FROM remediation_groups WHERE audit_id=? ORDER BY priority_score DESC,group_id", (audit_id,))
        recommendations = _optional(connection, "SELECT * FROM recommendations WHERE audit_id=? ORDER BY priority_score DESC,recommendation_id", (audit_id,))
        semantic = _optional(connection, """
            SELECT sa.*,ps.device,ps.page_id,p.normalized_url FROM semantic_assessments sa
            JOIN page_snapshots ps ON ps.snapshot_id=sa.snapshot_id
            JOIN pages p ON p.page_id=ps.page_id
            WHERE p.audit_id=? ORDER BY p.normalized_url,ps.device,sa.assessment_type
        """, (audit_id,))
        ai_session = None
        ai_attempts: list[sqlite3.Row] = []
        try:
            ai_session = connection.execute("SELECT * FROM ai_audit_sessions WHERE audit_id=?", (audit_id,)).fetchone()
            ai_attempts = list(connection.execute(
                "SELECT * FROM ai_provider_attempts WHERE audit_id=? ORDER BY started_at,attempt_index,attempt_id",
                (audit_id,),
            ).fetchall())
        except sqlite3.OperationalError:
            pass
        return {
            "audit": audit,
            "pages": pages,
            "snapshots": snapshots,
            "scores": scores,
            "findings": findings,
            "groups": groups,
            "recommendations": recommendations,
            "semantic": semantic,
            "ai_session": ai_session,
            "ai_attempts": ai_attempts,
        }
    finally:
        connection.close()


def _optional(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
    try:
        return list(connection.execute(sql, params).fetchall())
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower():
            return []
        raise


def _available_devices(data: dict[str, Any]) -> tuple[str, ...]:
    devices = {
        str(row["device"]).upper()
        for row in data["snapshots"]
        if row["device"] not in (None, "")
    }
    ordered = tuple(device for device in ("MOBILE", "DESKTOP") if device in devices)
    if ordered:
        return ordered
    score_devices = {str(row["device"]).upper() for row in data["scores"] if row["device"]}
    return tuple(device for device in ("MOBILE", "DESKTOP") if device in score_devices)


def _navigation(devices: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    items: list[tuple[str, str]] = [("Visão geral", INDEX_FILE)]
    if "MOBILE" in devices:
        items.append(("Relatório Mobile", MOBILE_FILE))
    if "DESKTOP" in devices:
        items.append(("Relatório Desktop", DESKTOP_FILE))
    items.extend((
        ("Remediações", REMEDIATION_FILE),
        ("Uso de IA", AI_FILE),
        ("Referências e metodologia", REFERENCES_FILE),
    ))
    return tuple(items)


def _shell(title: str, current: str, nav: tuple[tuple[str, str], ...], content: str) -> str:
    links = "".join(
        f"<a class='{'active' if filename == current else ''}' href='{escape(filename)}'>{escape(label)}</a>"
        for label, filename in nav
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escape(title)} — SearchGEO Readiness Auditor</title>
  <link rel="stylesheet" href="{CSS_FILE}">
</head>
<body>
  <aside class="app-nav" aria-label="Navegação do relatório">
    <div class="brand"><small>SearchGEO Auditor</small><strong>Relatório da auditoria</strong></div>
    <nav>{links}</nav>
  </aside>
  <main class="app-main">{content}<footer class="footer">Projeção estática derivada do audit.db. Scores e findings não são recalculados no HTML.</footer></main>
</body>
</html>
"""


def _overview(data: dict[str, Any], devices: tuple[str, ...]) -> str:
    audit = data["audit"]
    pages = data["pages"]
    findings = data["findings"]
    scores = data["scores"]

    action_counts: Counter[str] = Counter()
    for row in findings:
        action = classify_actionability(
            str(row["rule_result"]),
            rule_id=str(row["rule_id"]),
            observed_value=_json_object(row["execution_observed_value"]),
        )
        action_counts[action.value] += 1

    score_cards = "".join(_overall_card(scores, device) for device in devices)
    dimensions = "".join(_dimension_table(scores, device) for device in devices)

    required = action_counts[Actionability.REQUIRED_FIX.value]
    review = action_counts[Actionability.REVIEW_RECOMMENDED.value]
    insufficient = action_counts[Actionability.INSUFFICIENT_EVIDENCE.value]
    device_context = ", ".join(_device_label(item) for item in devices) or "Nenhum snapshot"
    return f"""
<header class="hero">
  <div class="eyebrow">SearchGEO Readiness Auditor</div>
  <h1>Visão geral da auditoria</h1>
  <p class="lead">Dashboard executivo de readiness GEO. O índice é um modelo interno e reprodutível do SearchGEO; não é uma nota oficial do Google, OpenAI ou de outro mantenedor.</p>
  <div class="score-grid">{score_cards or '<div class="notice">Score não disponível.</div>'}</div>
  <div class="metric-grid">
    {_metric("Projeto", audit["project_name"])}
    {_metric("Audit ID", audit["audit_id"])}
    {_metric("Páginas auditadas", len(pages))}
    {_metric("Contexto de dispositivo", device_context)}
    {_metric("Ações necessárias", required)}
    {_metric("Revisões recomendadas", review)}
    {_metric("Evidência insuficiente", insufficient)}
  </div>
</header>
<section class="panel">
  <div class="kicker">Leitura obrigatória</div>
  <h2>Cobertura e confiabilidade</h2>
  <p class="intro"><strong>Confiabilidade baixa não significa que o texto do website é ruim ou “não aderente a GEO”.</strong> Ela indica que a força da conclusão do auditor é limitada por cobertura, disponibilidade/qualidade das evidências, erros de execução ou estados UNKNOWN. O conteúdo do website é julgado pelo Score e pelos findings; a confiabilidade qualifica o quanto podemos sustentar essa conclusão.</p>
  <div class="confidence-explain">
    <div><strong>Score / Readiness</strong><p>Qualidade observada somente nas regras efetivamente avaliadas. FAIL reduz a nota; WARNING reduz parcialmente; UNKNOWN/ERROR não são tratados como FAIL.</p></div>
    <div><strong>Coverage</strong><p>Proporção do peso aplicável realmente avaliado. Cobertura baixa significa análise incompleta, não qualidade baixa do site.</p></div>
    <div><strong>Confidence</strong><p>Força da conclusão. LOW pede cautela na interpretação e normalmente justifica ampliar evidências ou resolver limitações da auditoria.</p></div>
  </div>
  <div class="notice warn"><strong>Importante:</strong> um score alto com confiança baixa não deve ser comunicado como “site aprovado sem ressalvas”. O dashboard mantém os dois indicadores separados e usa cor própria para a força da conclusão.</div>
</section>
<section class="panel">
  <div class="panel-head"><div><div class="kicker">Dimensões</div><h2>Readiness por dispositivo</h2></div></div>
  {dimensions or '<p class="intro">Nenhuma dimensão de score persistida.</p>'}
</section>
<section class="panel">
  <div class="kicker">Próximos passos</div>
  <h2>Navegação do relatório</h2>
  <div class="grid">
    <div class="ref-card"><h3>Relatório por dispositivo</h3><p>Use Mobile ou Desktop no menu para inspecionar páginas, snapshots, findings e avaliações semânticas sem misturar contextos.</p></div>
    <div class="ref-card"><h3>Remediações</h3><p>Consolida achados acionáveis por regra e prioridade, evitando duplicação de correções entre páginas.</p></div>
    <div class="ref-card"><h3>Uso de IA</h3><p>Telemetria operacional fica separada do readiness do website para não confundir falha de provider com falha GEO.</p></div>
    <div class="ref-card"><h3>Referências</h3><p>Documenta fontes oficiais, regras internas e fórmulas de cálculo usadas pelo programa.</p></div>
  </div>
</section>
"""


def _overall_card(scores: list[sqlite3.Row], device: str) -> str:
    row = next((item for item in scores if str(item["device"]).upper() == device and item["dimension"] == "OVERALL_READINESS"), None)
    if row is None or row["value"] is None or str(row["consolidation_status"]) == "NOT_CONSOLIDATED":
        coverage = f"{float(row['coverage']) * 100:.0f}%" if row is not None else "—"
        return f"""<article class="score-card warn"><div class="label">{_device_label(device)}</div>
        <div class="score-number">Não consolidado</div>
        <p class="intro">Cobertura {escape(coverage)}. Não há base suficiente para publicar um readiness geral deste dispositivo.</p></article>"""
    score = float(row["value"])
    classification, score_state = _score_classification(score)
    confidence = str(row["confidence"])
    class_state = "good" if score_state == "success" else "warn" if score_state == "warning" else "bad"
    confidence_badge = _confidence_badge(confidence)
    return f"""<article class="score-card {class_state}">
      <div class="label">{_device_label(device)} · índice interno</div>
      <div class="score-number">{score:.1f}<span>/100</span></div>
      <div><span class="badge {class_state}">{escape(classification)}</span> {confidence_badge}</div>
      <div class="score-meta">
        <div><small>Coverage</small><strong>{float(row['coverage']) * 100:.0f}%</strong></div>
        <div><small>Confidence</small><strong>{escape(_STATUS_LABELS.get(confidence, confidence))}</strong></div>
        <div><small>Consolidação</small><strong>{escape(_STATUS_LABELS.get(str(row['consolidation_status']), str(row['consolidation_status'])))}</strong></div>
      </div>
    </article>"""


def _confidence_badge(confidence: str) -> str:
    css = {"HIGH": "good", "MEDIUM": "info", "LOW": "warn", "UNAVAILABLE": "unknown"}.get(confidence, "unknown")
    label = _STATUS_LABELS.get(confidence, confidence)
    return f"<span class='badge {css}'>Confiança {escape(label.lower())}</span>"


def _dimension_table(scores: list[sqlite3.Row], device: str) -> str:
    rows = [
        row for row in scores
        if str(row["device"]).upper() == device and row["dimension"] != "OVERALL_READINESS"
    ]
    if not rows:
        return ""
    body = []
    for row in rows:
        score = "—" if row["value"] is None else f"{float(row['value']):.1f}"
        body.append(
            "<tr>"
            f"<td>{escape(_DIMENSION_LABELS.get(str(row['dimension']), str(row['dimension'])))}</td>"
            f"<td>{escape(score)}</td>"
            f"<td>{float(row['coverage']) * 100:.0f}%</td>"
            f"<td>{escape(_STATUS_LABELS.get(str(row['confidence']), str(row['confidence'])))}</td>"
            f"<td>{escape(_STATUS_LABELS.get(str(row['consolidation_status']), str(row['consolidation_status'])))}</td>"
            "</tr>"
        )
    return f"""<h3>{_device_label(device)}</h3><div class="table-wrap"><table>
      <thead><tr><th>Dimensão</th><th>Score</th><th>Coverage</th><th>Confidence</th><th>Consolidação</th></tr></thead>
      <tbody>{''.join(body)}</tbody></table></div>"""


def _device_page(data: dict[str, Any], device: str) -> str:
    snapshots = [row for row in data["snapshots"] if str(row["device"]).upper() == device]
    snapshot_by_page = {str(row["page_id"]): row for row in snapshots}
    findings_by_page: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in data["findings"]:
        value = str(row["device"] or "").upper()
        if value in {device, "BOTH"} and row["page_id"]:
            findings_by_page[str(row["page_id"])].append(row)
    semantic_by_page: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in data["semantic"]:
        if str(row["device"]).upper() == device:
            semantic_by_page[str(row["page_id"])].append(row)

    page_cards = []
    for page in data["pages"]:
        page_id = str(page["page_id"])
        snapshot = snapshot_by_page.get(page_id)
        if snapshot is None:
            continue
        page_cards.append(_page_card(page, snapshot, findings_by_page.get(page_id, []), semantic_by_page.get(page_id, []), device))

    return f"""
<header class="hero">
  <div class="eyebrow">Relatório por dispositivo</div>
  <h1>{_device_label(device)}</h1>
  <p class="lead">Visão isolada do contexto {_device_label(device).lower()}. Findings de outro dispositivo não são misturados nesta página.</p>
  <div class="score-grid">{_overall_card(data["scores"], device)}</div>
</header>
<section class="panel">
  <div class="kicker">Scorecard</div><h2>Dimensões {_device_label(device)}</h2>
  {_dimension_table(data["scores"], device)}
</section>
<section class="panel">
  <div class="kicker">Páginas</div><h2>Auditoria por URL</h2>
  {''.join(page_cards) if page_cards else '<p class="intro">Nenhum snapshot disponível para este dispositivo.</p>'}
</section>
"""


def _page_card(page: sqlite3.Row, snapshot: sqlite3.Row, findings: list[sqlite3.Row], semantic: list[sqlite3.Row], device: str) -> str:
    screenshot = _visual_ref(snapshot)
    screenshot_html = ""
    if screenshot:
        screenshot_html = (
            f"<figure><a href='../{escape(screenshot)}' target='_blank' rel='noopener'>"
            f"<img loading='lazy' src='../{escape(screenshot)}' alt='Screenshot {_device_label(device)}'></a>"
            f"<figcaption>Snapshot visual preservado</figcaption></figure>"
        )
    semantic_counts = Counter(str(row["result"]) for row in semantic)
    semantic_summary = " · ".join(
        f"{_STATUS_LABELS.get(key, key)}: {value}" for key, value in sorted(semantic_counts.items())
    ) or "Sem avaliações semânticas persistidas"
    findings_html = "".join(_finding_detail(row) for row in findings)
    semantic_html = "".join(_semantic_detail(row) for row in semantic if str(row["result"]) != "PASS")
    return f"""
<article class="page-card">
  <div class="kicker">Página auditada</div>
  <h3 class="page-url">{escape(str(page["normalized_url"]))}</h3>
  <div class="page-summary">
    <div><small>HTTP</small><strong>{escape(str(snapshot["http_status"] if snapshot["http_status"] is not None else "—"))}</strong></div>
    <div><small>Final URL</small><strong>{escape(str(snapshot["final_url"] or "—"))}</strong></div>
    <div><small>Findings</small><strong>{len(findings)}</strong></div>
    <div><small>Semântica</small><strong>{escape(semantic_summary)}</strong></div>
  </div>
  <div class="snapshot">{screenshot_html}<div>
    <h4>Findings desta URL</h4>{findings_html or '<p class="intro">Nenhum finding acionável persistido para este dispositivo.</p>'}
    <h4>Avaliações semânticas não aprovadas</h4>{semantic_html or '<p class="intro">Nenhuma avaliação semântica não aprovada persistida.</p>'}
  </div></div>
</article>
"""


def _finding_detail(row: sqlite3.Row) -> str:
    action = classify_actionability(
        str(row["rule_result"]),
        rule_id=str(row["rule_id"]),
        observed_value=_json_object(row["execution_observed_value"]),
    )
    action_css = {
        Actionability.REQUIRED_FIX: "bad",
        Actionability.REVIEW_RECOMMENDED: "warn",
        Actionability.OPTIONAL_IMPROVEMENT: "info",
        Actionability.NO_ACTION: "good",
        Actionability.INSUFFICIENT_EVIDENCE: "unknown",
    }[action]
    observed = _pretty_json(row["execution_observed_value"])
    evidence_ids = ", ".join(str(item) for item in _json_list(row["evidence_ids"])) or "—"
    return f"""
<div class="finding">
  <div class="finding-head"><span class="finding-title">{escape(str(row["title"]))}</span>
    <span><span class="badge {action_css}">{escape(label_for(action))}</span> <span class="badge">{escape(str(row["rule_id"]))}</span></span>
  </div>
  <details><summary>Diagnóstico e evidências</summary>
    <p><strong>Resultado:</strong> {escape(_STATUS_LABELS.get(str(row["rule_result"]), str(row["rule_result"])))}</p>
    <p><strong>Condição esperada:</strong> {escape(str(row["expected_condition"] or "—"))}</p>
    <p><strong>Evidências:</strong> <span class="mono">{escape(evidence_ids)}</span></p>
    <pre>{escape(observed)}</pre>
  </details>
</div>
"""


def _semantic_detail(row: sqlite3.Row) -> str:
    summary = str(row["reasoning_summary"] or row["assessment_type"])
    confidence = float(row["confidence"]) * 100 if row["confidence"] is not None else 0.0
    return f"""
<details>
  <summary>{escape(str(row["assessment_type"]))} · {escape(_STATUS_LABELS.get(str(row["result"]), str(row["result"])))}</summary>
  <p>{escape(summary)}</p>
  <p class="intro">Confiabilidade da avaliação semântica normalizada: {confidence:.0f}% · provider {escape(str(row["provider"] or "—"))}</p>
</details>
"""


def _remediation_page(data: dict[str, Any]) -> str:
    groups = data["groups"]
    recommendations = data["recommendations"]
    rec_by_group = {
        str(row["remediation_group_id"]): row
        for row in recommendations if row["remediation_group_id"]
    }
    finding_by_id = {str(row["finding_id"]): row for row in data["findings"]}
    cards = []
    for group in groups:
        finding_ids = [str(item) for item in _json_list(group["affected_findings"])]
        sample = next((finding_by_id.get(item) for item in finding_ids if finding_by_id.get(item)), None)
        rec = rec_by_group.get(str(group["group_id"]))
        title = str(rec["title"] if rec is not None else (sample["title"] if sample is not None else group["root_cause"]))
        description = str(rec["description"] if rec is not None else group["root_cause"])
        priority = str(group["priority_class"])
        priority_css = "bad" if priority in {"P0", "P1"} else "warn" if priority == "P2" else "info"
        affected_pages = [str(item) for item in _json_list(group["affected_pages"])]
        refs = "".join(_reference_links(str(group["rule_id"])))
        cards.append(f"""
        <article class="page-card">
          <div class="finding-head"><div><span class="badge {priority_css}">{escape(priority)}</span> <span class="badge">{escape(str(group["rule_id"]))}</span></div>
          <span class="badge">{len(finding_ids)} ocorrência(s)</span></div>
          <h3>{escape(title)}</h3>
          <p>{escape(description)}</p>
          <div class="page-summary">
            <div><small>Impacto</small><strong>{escape(str(group["impact"]))}</strong></div>
            <div><small>Esforço</small><strong>{escape(str(group["effort"]))}</strong></div>
            <div><small>Confiança da prioridade</small><strong>{escape(str(group["confidence"]))}</strong></div>
            <div><small>Páginas afetadas</small><strong>{len(affected_pages)}</strong></div>
          </div>
          <details><summary>URLs e referências técnicas</summary>
            <p class="mono">{'<br>'.join(escape(item) for item in affected_pages) or 'Escopo global'}</p>
            <div>{refs or '<span class="intro">Regra de baseline interna sem fonte normativa específica.</span>'}</div>
          </details>
        </article>""")
    return f"""
<header class="hero"><div class="eyebrow">Plano acionável</div><h1>Remediações</h1>
<p class="lead">Agrupamento por causa/regra e prioridade. Esta página evita repetir a mesma orientação para cada ocorrência quando a causa raiz é compartilhada.</p></header>
<section class="panel"><div class="kicker">Prioridades</div><h2>Achados agrupados</h2>
{''.join(cards) if cards else '<p class="intro">Nenhum grupo de remediação persistido.</p>'}</section>
"""


def _ai_page(data: dict[str, Any]) -> str:
    session = data["ai_session"]
    attempts = data["ai_attempts"]
    if session is None:
        return """<header class="hero"><div class="eyebrow">Telemetria operacional</div><h1>Uso de IA</h1>
        <p class="lead">Esta auditoria não possui uma sessão M18 persistida.</p></header>"""
    success = [row for row in attempts if str(row["status"]) == "SUCCESS"]
    total_cost = sum(float(row["estimated_cost"]) for row in attempts if row["estimated_cost"] is not None)
    rows = []
    for row in attempts:
        status = str(row["status"])
        css = "good" if status == "SUCCESS" else "warn"
        error = " · ".join(str(row[key]) for key in ("error_class", "http_status", "error_code") if row[key] not in (None, "")) or "—"
        estimated = f"{float(row['estimated_cost']):.8f}" if row["estimated_cost"] is not None else "—"
        rows.append(
            "<tr>"
            f"<td class='mono'>{escape(str(row['url']))}</td>"
            f"<td>{escape(str(row['device'] or '—'))}</td>"
            f"<td>{escape(str(row['provider']))}</td>"
            f"<td>{escape(str(row['model'] or '—'))}</td>"
            f"<td><span class='badge {css}'>{escape(status)}</span></td>"
            f"<td>{escape(str(row['input_tokens'] if row['input_tokens'] is not None else '—'))}</td>"
            f"<td>{escape(str(row['output_tokens'] if row['output_tokens'] is not None else '—'))}</td>"
            f"<td>{escape(str(row['reasoning_tokens'] if row['reasoning_tokens'] is not None else '—'))}</td>"
            f"<td>{escape(estimated)}</td>"
            f"<td>{escape(str(row['duration_ms']))} ms</td>"
            f"<td>{escape(error)}</td>"
            "</tr>"
        )
    configured_chain = _json_list(session["configured_chain"])
    chain = " → ".join(
        f"{item.get('provider','?')} / {item.get('model','?')}" for item in configured_chain if isinstance(item, dict)
    ) or "Nenhum provider elegível"
    effective = f"{session['effective_provider']} / {session['effective_model']}" if session["effective_provider"] else "Nenhum resultado semântico válido"
    return f"""
<header class="hero">
  <div class="eyebrow">Telemetria operacional</div><h1>Uso de IA</h1>
  <p class="lead">Provider, tokens, custo estimado e failover são dados operacionais da auditoria. Falha de IA não é finding do website e não deve ser interpretada como penalização GEO.</p>
  <div class="metric-grid">
    {_metric("IA habilitada", "Sim" if bool(session["enabled"]) else "Não")}
    {_metric("Estratégia", session["strategy"])}
    {_metric("Provider efetivo", effective)}
    {_metric("Status da sessão", session["status"])}
    {_metric("Chamadas", len(attempts))}
    {_metric("Sucessos", len(success))}
    {_metric("Custo estimado total", f"{total_cost:.8f} USD")}
  </div>
</header>
<section class="panel"><h2>Roteamento</h2><p><strong>Cadeia inicial:</strong> {escape(chain)}</p>
<div class="notice"><strong>Sem sobrescrita:</strong> quando um contexto URL/dispositivo obtém resultado válido, o roteador encerra a cadeia para aquele contexto. Providers posteriores não devem sobrescrever a avaliação já aceita.</div></section>
<section class="panel"><h2>Tentativas</h2><div class="table-wrap"><table>
<thead><tr><th>URL</th><th>Device</th><th>Provider</th><th>Modelo</th><th>Status</th><th>Input</th><th>Output</th><th>Reasoning</th><th>Custo est.</th><th>Duração</th><th>Erro</th></tr></thead>
<tbody>{''.join(rows) if rows else '<tr><td colspan="11">Nenhuma chamada externa.</td></tr>'}</tbody></table></div>
<p class="intro">Estimated cost usa catálogo local versionado e não substitui billing/invoice do provider.</p></section>
"""


def _references_page() -> str:
    catalog_cards = "".join(
        f"""<article class="ref-card"><div class="kicker">{escape(authority)}</div><h3>{escape(title)}</h3>
        <p>{escape(scope)}</p><a href="{escape(url)}" target="_blank" rel="noopener">{escape(url)}</a></article>"""
        for authority, title, url, scope in _OFFICIAL_REFERENCE_CATALOG
    )
    rule_rows = []
    seen: set[tuple[str, str]] = set()
    for number in range(1, 55):
        rule_id = f"BR-GEO-{number:03d}"
        for ref in references_for(rule_id):
            key = (rule_id, ref.url or "")
            if key in seen:
                continue
            seen.add(key)
            if ref.url:
                source = f"<a href='{escape(ref.url)}' target='_blank' rel='noopener'>{escape((ref.authority or '') + ' — ' + (ref.title or ''))}</a>"
            else:
                source = "Baseline interna / heurística do SearchGEO"
            rule_rows.append(
                f"<tr><td>{escape(rule_id)}</td><td>{escape(ref.basis)}</td><td>{source}</td><td>{escape(ref.reference_scope)}</td></tr>"
            )
    return f"""
<header class="hero">
  <div class="eyebrow">Fundamentação técnica</div><h1>Referências e metodologia</h1>
  <p class="lead">GEO e AEO não possuem hoje um score normativo universal equivalente a uma especificação formal. O SearchGEO combina requisitos técnicos oficiais de HTTP, robots, HTML, canonicalização e dados estruturados com heurísticas internas de readiness semântico. Toda heurística é identificada como tal; ela não é apresentada como regra oficial de Google, OpenAI ou outro mantenedor.</p>
  <div class="notice"><strong>Última verificação do catálogo interno de referências:</strong> {escape(VERIFIED_ON)}. A documentação oficial deve prevalecer quando um mantenedor atualizar seu comportamento.</div>
</header>
<section class="panel"><div class="kicker">Fontes primárias</div><h2>Documentação oficial utilizada</h2><div class="ref-grid">{catalog_cards}</div></section>
<section class="panel">
  <div class="kicker">SCORE-GEO-002</div><h2>Regras de cálculo</h2>
  <div class="grid">
    <div class="ref-card"><h3>Dimension Score</h3><p><code>Σ(weight × result_factor) / Σ(weight evaluated) × 100</code></p><p>PASS=1, WARNING=0,5 por padrão, FAIL=0. UNKNOWN/ERROR/NOT_APPLICABLE não são convertidos em FAIL.</p></div>
    <div class="ref-card"><h3>Coverage</h3><p><code>evaluated applicable weight / total applicable weight</code></p><p>Expressa quanto do universo aplicável foi realmente avaliado.</p></div>
    <div class="ref-card"><h3>Confidence</h3><p>É a força da conclusão do auditor, derivada de coverage, evidência e erros de execução. <strong>Não é uma nota de qualidade do texto.</strong></p></div>
    <div class="ref-card"><h3>Overall</h3><p>Média simples entre dimensões aplicáveis com materialização suficiente. Dimensões legitimamente NOT_APPLICABLE são excluídas, não recebem zero nem cem.</p></div>
  </div>
  <div class="notice warn"><strong>Faixas “Excelente / Alta / Moderada / Baixa / Crítica” são classificação interna de apresentação.</strong> Não existe documentação oficial dos mantenedores que defina esses thresholds como padrão GEO universal.</div>
</section>
<section class="panel"><div class="kicker">Rastreabilidade por regra</div><h2>Fonte e natureza das BR-GEO</h2>
<div class="table-wrap"><table><thead><tr><th>Regra</th><th>Base</th><th>Fonte</th><th>Escopo</th></tr></thead><tbody>{''.join(rule_rows)}</tbody></table></div></section>
"""


def _reference_links(rule_id: str) -> list[str]:
    result = []
    for ref in references_for(rule_id):
        if ref.url:
            result.append(
                f"<a href='{escape(ref.url)}' target='_blank' rel='noopener'>{escape((ref.authority or '') + ' — ' + (ref.title or ''))}</a><br>"
            )
    return result


def _visual_ref(snapshot: sqlite3.Row) -> str | None:
    raw = snapshot["browser_metadata"]
    if raw in (None, ""):
        return None
    try:
        metadata = json.loads(str(raw))
    except json.JSONDecodeError:
        return None
    ref = metadata.get("visual_artifact_ref") if isinstance(metadata, dict) else None
    return str(ref) if ref else None


def _metric(label: str, value: Any) -> str:
    return f"<div class='metric'><small>{escape(str(label))}</small><strong>{escape(str(value))}</strong></div>"


def _device_label(device: str) -> str:
    return {"MOBILE": "Mobile", "DESKTOP": "Desktop"}.get(device, device.title())


def _json_list(value: Any) -> list[Any]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return []
    return parsed if isinstance(parsed, list) else []


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value in (None, ""):
        return {}
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


_SENSITIVE_KEY = re.compile(r"(?:api[_-]?key|authorization|password|secret|token|credential)", re.I)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): "[REDACTED]" if _SENSITIVE_KEY.search(str(k)) else _redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _pretty_json(value: Any) -> str:
    parsed: Any = value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = value
    parsed = _redact(parsed)
    if isinstance(parsed, (dict, list)):
        return json.dumps(parsed, ensure_ascii=False, indent=2, sort_keys=True)
    return str(parsed)
