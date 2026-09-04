"""Projection of M20 data into the static report site."""

from __future__ import annotations

from collections import defaultdict
from html import escape
import json
from pathlib import Path
import sqlite3
from typing import Any

from searchgeo.persistence import AuditWorkspace
from searchgeo.report_navigation import normalize_report_navigation, render_report_navigation

CONTENT_FILE = "content-suggestions.html"


def enrich_m20_report_site(*, audit_id: str, workspace: AuditWorkspace) -> Path:
    """Write the M20 page and connect it to the already materialized report site."""
    report_dir = workspace.root / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    data = _load(audit_id, workspace)
    content_path = report_dir / CONTENT_FILE
    content_path.write_text(_content_page(data, report_dir), encoding="utf-8", newline="\n")

    for html_path in report_dir.glob("*.html"):
        if html_path.name == CONTENT_FILE:
            continue
        html = html_path.read_text(encoding="utf-8")
        if html_path.name == "remediation.html" and "m20-content-link" not in html:
            html = html.replace(
                "</header>",
                "</header><section id='m20-content-link' class='notice'><strong>Conteúdo e Structured Data:</strong> "
                f"<a href='{CONTENT_FILE}'>abrir sugestões opcionais de conteúdo e revisão JSON-LD por página →</a></section>",
                1,
            )
        if html_path.name == "ai-usage.html" and "m20-ai-telemetry" not in html:
            html = html.replace("</main>", _ai_telemetry(data) + "</main>", 1)
        html_path.write_text(html, encoding="utf-8", newline="\n")

    normalize_report_navigation(report_dir)
    return content_path


def _load(audit_id: str, workspace: AuditWorkspace) -> dict[str, Any]:
    connection = sqlite3.connect(workspace.database)
    connection.row_factory = sqlite3.Row
    try:
        run = _one(connection, "SELECT * FROM content_remediation_runs WHERE audit_id=?", (audit_id,))
        suggestions = _many(connection, """
            SELECT s.*,p.normalized_url,f.rule_id,f.title AS finding_title
            FROM content_remediation_suggestions s
            JOIN pages p ON p.page_id=s.page_id
            JOIN findings f ON f.finding_id=s.finding_id
            WHERE s.audit_id=? ORDER BY p.normalized_url,s.device,f.rule_id,s.suggestion_id
        """, (audit_id,))
        jsonld = _many(connection, """
            SELECT j.*,p.normalized_url
            FROM jsonld_remediation_suggestions j
            JOIN pages p ON p.page_id=j.page_id
            WHERE j.audit_id=? ORDER BY p.normalized_url,j.device,j.suggestion_id
        """, (audit_id,))
        attempts = _many(connection, "SELECT * FROM content_remediation_attempts WHERE audit_id=? ORDER BY started_at,attempt_index,attempt_id", (audit_id,))
        return {"run": run, "suggestions": suggestions, "jsonld": jsonld, "attempts": attempts}
    finally:
        connection.close()


def _one(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> sqlite3.Row | None:
    try:
        return connection.execute(sql, params).fetchone()
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower():
            return None
        raise


def _many(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
    try:
        return list(connection.execute(sql, params).fetchall())
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower():
            return []
        raise


def _content_page(data: dict[str, Any], report_dir: Path) -> str:
    run = data["run"]
    nav = _nav(report_dir)
    run_status = str(run["status"]) if run is not None else "UNAVAILABLE"
    enabled = bool(run["enabled"]) if run is not None else False
    eligible = int(run["eligible_findings"]) if run is not None else 0
    generated = int(run["generated_suggestions"]) if run is not None else 0
    attempted = int(run["attempted_contexts"]) if run is not None else 0

    by_page: dict[tuple[str, str], list[sqlite3.Row]] = defaultdict(list)
    for row in data["suggestions"]:
        by_page[(str(row["normalized_url"]), str(row["device"]))].append(row)
    suggestion_cards = []
    for (url, device), rows in by_page.items():
        items = []
        for row in rows:
            evidence = ", ".join(_json_list(row["evidence_ids"])) or "—"
            items.append(f"""<details><summary>{escape(str(row['rule_id']))} · {escape(str(row['finding_title']))}</summary><div class='detail-body'><p><strong>Objetivo:</strong> {escape(str(row['objective']))}</p><p><strong>Local sugerido:</strong> {escape(str(row['target_location']))}</p><h5>Texto proposto</h5><pre>{escape(str(row['proposed_text']))}</pre><div class='remediation-grid'><div><small>Provider/model</small><strong>{escape(str(row['provider']))} / {escape(str(row['model'] or '—'))}</strong></div><div><small>Confiança da sugestão</small><strong>{float(row['confidence'])*100:.0f}%</strong></div><div><small>Evidências</small><strong class='mono'>{escape(evidence)}</strong></div></div><div class='notice warn'><strong>Revisão humana obrigatória:</strong> {escape(str(row['review_note']))}</div></div></details>""")
        suggestion_cards.append(f"<article class='page-card'><div class='kicker'>Sugestões de conteúdo · {escape(device)}</div><h3 class='page-url'>{escape(url)}</h3>{''.join(items)}</article>")

    jsonld_cards = []
    for row in data["jsonld"]:
        improvements = "".join(f"<li>{escape(str(item))}</li>" for item in _json_list(row["improvements"]))
        types = ", ".join(_json_list(row["existing_types"])) or "Nenhum tipo observado"
        proposed = ""
        if row["proposed_json"]:
            proposed_obj = _json_value(row["proposed_json"])
            proposed = f"<h5>JSON-LD baseline sugerido</h5><pre>{escape(json.dumps(proposed_obj, ensure_ascii=False, indent=2, sort_keys=True))}</pre>"
        jsonld_cards.append(f"""<article class='page-card'><div class='finding-head'><div><span class='badge'>{escape(str(row['device']))}</span> <span class='badge info'>{escape(str(row['status']))}</span></div><span class='badge'>{escape(types)}</span></div><h3 class='page-url'>{escape(str(row['normalized_url']))}</h3>{proposed}<h5>Revisão recomendada</h5><ul>{improvements}</ul></article>""")

    if not enabled:
        ai_notice = "<div class='notice'><strong>Sugestões de conteúdo por IA estão desabilitadas.</strong> Esse é o comportamento padrão. A revisão JSON-LD abaixo é determinística e não exige IA.</div>"
    elif run_status == "NOT_CONFIGURED":
        ai_notice = "<div class='notice warn'><strong>Remediação por IA foi habilitada, mas não havia provider saudável/configurado.</strong> Nenhuma sugestão textual externa foi publicada; a revisão JSON-LD determinística continua disponível.</div>"
    else:
        ai_notice = "<div class='notice warn'><strong>Conteúdo sugerido é proposta, não correção automática.</strong> Não altera score/findings e requer validação humana antes de publicação.</div>"

    return f"""<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Conteúdo e JSON-LD — SearchGEO Readiness Auditor</title><link rel='stylesheet' href='css/site.css'></head><body>{nav}<main class='app-main'><header class='hero'><div class='eyebrow'>M20 · remediação opcional</div><h1>Conteúdo e JSON-LD</h1><p class='lead'>Sugestões textuais são evidence-bound, opcionais e desligadas por padrão. JSON-LD é analisado separadamente como reforço de Structured Data; não é requisito universal de GEO nem garantia de rich result.</p><div class='metric-grid'>{_metric('Remediação por IA','Habilitada' if enabled else 'Desabilitada')}{_metric('Status',run_status)}{_metric('Findings elegíveis',eligible)}{_metric('Contextos chamados',attempted)}{_metric('Sugestões publicadas',generated)}{_metric('Revisões JSON-LD',len(data['jsonld']))}</div></header>{ai_notice}<section class='panel'><div class='kicker'>People-first</div><h2>Sugestões textuais por finding</h2><p class='intro'>Confidence LOW do score, sozinha, nunca dispara esta etapa. Só findings semânticos/contentuais persistidos entram no input. O contrato bloqueia evidence_ids externos ao finding e rejeita novos tokens numéricos que não existam no conteúdo/evidências fornecidos.</p>{''.join(suggestion_cards) if suggestion_cards else '<p class="intro">Nenhuma sugestão textual persistida.</p>'}</section><section class='panel'><div class='kicker'>Structured Data</div><h2>JSON-LD por página/dispositivo</h2><p class='intro'>Quando não há JSON-LD, o auditor propõe um baseline <code>WebPage</code> usando somente URL, idioma, title, description e, quando inequívoca, uma entidade já observada com alta confiança. Quando já existe markup, o auditor não o sobrescreve: aponta problemas estruturais genéricos e melhorias seguras. Para rich results, valide também a documentação específica do tipo.</p><div class='notice'><strong>Referências:</strong> Google recomenda JSON-LD como um dos formatos suportados e exige que Structured Data represente fielmente conteúdo visível. <a href='https://developers.google.com/search/docs/appearance/structured-data/sd-policies' target='_blank' rel='noopener'>General Structured Data Guidelines</a> · <a href='https://schema.org/docs/documents.html' target='_blank' rel='noopener'>Schema.org</a>.</div>{''.join(jsonld_cards) if jsonld_cards else '<p class="intro">Nenhuma revisão JSON-LD persistida.</p>'}</section><footer class='footer'>M20 é projeção auxiliar. Nenhuma sugestão altera retrospectivamente RuleExecution, Finding, Score, Coverage ou Confidence.</footer></main></body></html>\n"""


def _nav(report_dir: Path) -> str:
    return render_report_navigation(report_dir, CONTENT_FILE)


def _ai_telemetry(data: dict[str, Any]) -> str:
    attempts = data["attempts"]
    run = data["run"]
    total_cost = sum(float(row["estimated_cost"]) for row in attempts if row["estimated_cost"] is not None)
    rows = []
    for row in attempts:
        error = " · ".join(str(row[key]) for key in ("error_class", "http_status", "error_code") if row[key] not in (None, "")) or "—"
        cost = f"{float(row['estimated_cost']):.8f}" if row["estimated_cost"] is not None else "—"
        rows.append(f"<tr><td class='mono'>{escape(str(row['url']))}</td><td>{escape(str(row['device']))}</td><td>{escape(str(row['provider']))}</td><td>{escape(str(row['model'] or '—'))}</td><td>{escape(str(row['status']))}</td><td>{escape(str(row['input_tokens'] if row['input_tokens'] is not None else '—'))}</td><td>{escape(str(row['output_tokens'] if row['output_tokens'] is not None else '—'))}</td><td>{escape(cost)}</td><td>{escape(str(row['duration_ms']))} ms</td><td>{escape(error)}</td></tr>")
    status = str(run["status"]) if run is not None else "UNAVAILABLE"
    enabled = bool(run["enabled"]) if run is not None else False
    return f"""<section id='m20-ai-telemetry' class='panel'><div class='kicker'>M20</div><h2>Remediação opcional de conteúdo por IA</h2><p class='intro'>Telemetria desta segunda finalidade é separada da análise semântica M18. O recurso é default OFF e não executa chamadas apenas porque Confidence está baixa.</p><div class='metric-grid'>{_metric('Habilitada','Sim' if enabled else 'Não')}{_metric('Status',status)}{_metric('Chamadas',len(attempts))}{_metric('Custo estimado',f'{total_cost:.8f} USD')}</div><div class='table-wrap'><table><thead><tr><th>URL</th><th>Device</th><th>Provider</th><th>Modelo</th><th>Status</th><th>Input</th><th>Output</th><th>Custo est.</th><th>Duração</th><th>Erro</th></tr></thead><tbody>{''.join(rows) if rows else '<tr><td colspan="10">Nenhuma chamada M20.</td></tr>'}</tbody></table></div></section>"""


def _metric(label: str, value: Any) -> str:
    return f"<div class='metric'><small>{escape(str(label))}</small><strong>{escape(str(value))}</strong></div>"


def _json_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _json_list(value: Any) -> list[Any]:
    parsed = _json_value(value)
    return parsed if isinstance(parsed, list) else []