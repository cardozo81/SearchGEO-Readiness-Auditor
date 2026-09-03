"""M18 operational AI context for report.html and remediation.html."""

from __future__ import annotations

from html import escape
import json
import re
import sqlite3
from typing import Any

from searchgeo.persistence import AuditWorkspace


_CSS = """
<style>
.m18-ai{margin:2rem 0;padding:1.25rem;border:1px solid #d7dce2;border-radius:12px;background:#fff}
.m18-ai h2,.m18-ai h3{margin-top:.25rem}.m18-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.75rem;margin:1rem 0}
.m18-metric{padding:.75rem;border:1px solid #e2e6ea;border-radius:8px;min-width:0}.m18-metric strong{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.03em;margin-bottom:.3rem}
.m18-table-wrap{overflow-x:auto}.m18-ai table{border-collapse:collapse;width:100%;font-size:.86rem}.m18-ai th,.m18-ai td{border-bottom:1px solid #e5e7eb;padding:.55rem;text-align:left;vertical-align:top;white-space:nowrap}
.m18-ai td.m18-error{max-width:28rem;overflow:hidden;text-overflow:ellipsis}.m18-note{font-size:.9rem;color:#4b5563}
</style>
"""


def enrich_report_html(html: str, *, audit_id: str, workspace: AuditWorkspace) -> str:
    session, attempts, snapshot_count = _load(audit_id, workspace)
    if session is None:
        return html
    html = _correct_legacy_ai_metrics(html, session, attempts)
    block = _CSS + _report_section(session, attempts, snapshot_count)
    return _insert_before_body(html, block)


def enrich_remediation_html(html: str, *, audit_id: str, workspace: AuditWorkspace) -> str:
    session, attempts, snapshot_count = _load(audit_id, workspace)
    if session is None:
        return html
    block = _CSS + _remediation_context(session, attempts, snapshot_count)
    return _insert_before_body(html, block)


def enrich_written_reports(*, audit_id: str, workspace: AuditWorkspace) -> None:
    """Enrich the two static M11 projections after they are materialized."""

    report = workspace.root / "report.html"
    remediation = workspace.root / "remediation.html"
    if report.is_file():
        report.write_text(enrich_report_html(report.read_text(encoding="utf-8"), audit_id=audit_id, workspace=workspace), encoding="utf-8")
    if remediation.is_file():
        remediation.write_text(enrich_remediation_html(remediation.read_text(encoding="utf-8"), audit_id=audit_id, workspace=workspace), encoding="utf-8")


def _provider_configured(session: sqlite3.Row) -> bool:
    return bool(session["enabled"]) and str(session["status"]) != "NOT_CONFIGURED"


def _correct_legacy_ai_metrics(html: str, session: sqlite3.Row, attempts: list[sqlite3.Row]) -> str:
    success = [row for row in attempts if row["status"] == "SUCCESS"]
    if success:
        usage = "SIM"
    elif attempts:
        usage = "TENTATIVA SEM SUCESSO"
    else:
        usage = "NÃO"
    html = re.sub(
        r"(<div class='metric'><small>Uso de IA</small><strong>)(.*?)(</strong></div>)",
        lambda match: match.group(1) + escape(usage) + match.group(3),
        html,
        count=1,
    )
    if success:
        models = sorted({str(row["model"]) for row in success if row["model"]})
        model_display = ", ".join(models) or "NÃO APLICÁVEL"
    elif str(session["status"]) == "NOT_CONFIGURED":
        model_display = str(session["initial_model"] or "NÃO CONFIGURADO") + " · PROVIDER NÃO CONFIGURADO"
    elif bool(session["enabled"]):
        model_display = str(session["initial_model"] or "CONFIGURADO · NÃO CONFIRMADO PELA API")
    else:
        model_display = "NÃO APLICÁVEL"
    html = re.sub(
        r"(<div class='metric'><small>Modelo</small><strong>)(.*?)(</strong></div>)",
        lambda match: match.group(1) + escape(model_display) + match.group(3),
        html,
        count=1,
    )
    return html


def _load(audit_id: str, workspace: AuditWorkspace) -> tuple[sqlite3.Row | None, list[sqlite3.Row], int]:
    connection = sqlite3.connect(workspace.database)
    connection.row_factory = sqlite3.Row
    try:
        try:
            session = connection.execute("SELECT * FROM ai_audit_sessions WHERE audit_id=?", (audit_id,)).fetchone()
            attempts = list(connection.execute(
                "SELECT * FROM ai_provider_attempts WHERE audit_id=? ORDER BY started_at,attempt_index,attempt_id",
                (audit_id,),
            ).fetchall())
        except sqlite3.OperationalError:
            return None, [], 0
        snapshot_count = int(connection.execute(
            """SELECT COUNT(*) FROM page_snapshots ps JOIN pages p ON p.page_id=ps.page_id WHERE p.audit_id=?""",
            (audit_id,),
        ).fetchone()[0])
        return session, attempts, snapshot_count
    finally:
        connection.close()


def _report_section(session: sqlite3.Row, attempts: list[sqlite3.Row], snapshot_count: int) -> str:
    enabled = bool(session["enabled"])
    configured = _provider_configured(session)
    success = [row for row in attempts if row["status"] == "SUCCESS"]
    provider_counts: dict[str, set[str]] = {}
    for row in success:
        provider_counts.setdefault(str(row["provider"]), set()).add(str(row["url"]))
    counts_html = "<br>".join(f"{escape(provider)}: {len(urls)}" for provider, urls in sorted(provider_counts.items())) or "NENHUMA"
    configured_chain = _json_list(session["configured_chain"])
    initial = _provider_label(session["initial_provider"], session["initial_model"])
    effective = _provider_label(session["effective_provider"], session["effective_model"])
    if not session["effective_provider"]:
        effective = "NÃO HOUVE RESULTADO SEMÂNTICO VÁLIDO"

    metrics = (
        _metric("IA habilitada pelo comando", "SIM" if enabled else "NÃO")
        + _metric("Provider configurado", "SIM" if configured else "NÃO")
        + _metric("Estratégia", str(session["strategy"]))
        + _metric("Provider inicialmente selecionado", initial or "NÃO APLICÁVEL")
        + _metric("Provider efetivamente utilizado", effective)
        + _metric("Modelo efetivo", str(session["effective_model"] or "NÃO APLICÁVEL"))
        + _metric("Profundidade", str(session["effective_reasoning_profile"] or session["initial_reasoning_profile"] or "NÃO APLICÁVEL"))
        + _metric("Status", str(session["status"]))
        + _metric("Chamadas externas realizadas", str(len(attempts)))
        + _metric("Tentativas com sucesso", str(len(success)))
        + _metric("URLs analisadas com sucesso por provider", counts_html)
    )
    chain = " → ".join(
        f"{escape(str(item.get('provider','?')))} / {escape(str(item.get('model','?')))}"
        for item in configured_chain if isinstance(item, dict)
    ) or "NENHUMA IA ELEGÍVEL"
    failover = _failover_summary(attempts)
    rows = "".join(_attempt_row(row) for row in attempts)
    if not rows:
        rows = "<tr><td colspan='12'>Nenhuma chamada externa foi realizada.</td></tr>"
    coverage = f"{len(success)}/{snapshot_count} contextos Desktop/Mobile com tentativa bem-sucedida" if snapshot_count else "NÃO APLICÁVEL"
    return (
        "<section id='ai-runtime' class='m18-ai'>"
        "<h2>Uso de IA — execução e telemetria</h2>"
        "<p class='m18-note'>A indisponibilidade ou falta de configuração de um provider é limitação operacional da auditoria; não é finding GEO e não reduz o Score do website.</p>"
        f"<div class='m18-grid'>{metrics}</div>"
        f"<p><strong>Cadeia inicial imutável:</strong> {chain}</p>"
        f"<p><strong>Cobertura semântica externa:</strong> {escape(coverage)}</p>"
        f"<p><strong>Failover:</strong> {failover}</p>"
        "<h3>Relatório de uso da IA</h3><div class='m18-table-wrap'><table>"
        "<thead><tr><th>URL</th><th>Device</th><th>Provider</th><th>Model</th><th>Depth</th><th>Status</th><th>Tokens input</th><th>Tokens output</th><th>Tokens reasoning</th><th>Estimated cost</th><th>Duration</th><th>Error</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
        "<p class='m18-note'>ESTIMATED_COST usa catálogo versionado local e não representa invoice/billing do provider. Campos de tokens não reportados permanecem vazios.</p>"
        "</section>"
    )


def _remediation_context(session: sqlite3.Row, attempts: list[sqlite3.Row], snapshot_count: int) -> str:
    success = [row for row in attempts if row["status"] == "SUCCESS"]
    effective = _provider_label(session["effective_provider"], session["effective_model"])
    coverage = f"{len(success)}/{snapshot_count} contextos Desktop/Mobile" if snapshot_count else "NÃO APLICÁVEL"
    limitations: list[str] = []
    if session["status"] == "CHAIN_EXHAUSTED":
        limitations.append("AI_PROVIDER_CHAIN_EXHAUSTED")
    if session["status"] == "NOT_CONFIGURED":
        limitations.append("provider de IA selecionado, mas sem configuração/credencial elegível")
    if any(row["status"] != "SUCCESS" for row in attempts):
        limitations.append("houve tentativa(s) de provider sem resultado válido")
    if not bool(session["enabled"]):
        limitations.append("IA externa desabilitada")
    return (
        "<section id='ai-remediation-context' class='m18-ai'>"
        "<h2>Contexto da análise semântica</h2>"
        f"<p><strong>Provider configurado:</strong> {'SIM' if _provider_configured(session) else 'NÃO'}</p>"
        f"<p><strong>Provider efetivo:</strong> {escape(effective or 'NENHUM')}</p>"
        f"<p><strong>Chamadas externas:</strong> {len(attempts)}</p>"
        f"<p><strong>Cobertura semântica:</strong> {escape(coverage)}</p>"
        f"<p><strong>Limitações:</strong> {escape('; '.join(limitations) if limitations else 'NENHUMA LIMITAÇÃO DE PROVIDER COM IMPACTO DE COBERTURA')}</p>"
        "<p class='m18-note'>Este bloco é informativo. Falha de IA não é atribuída ao website e não cria finding nem recommendation GEO.</p>"
        "</section>"
    )


def _metric(label: str, value: str) -> str:
    # counts_html may intentionally contain <br>; all other values are escaped before input.
    safe_value = value if "<br>" in value else escape(value)
    return f"<div class='m18-metric'><strong>{escape(label)}</strong><span>{safe_value}</span></div>"


def _attempt_row(row: sqlite3.Row) -> str:
    error_parts = [str(row[key]) for key in ("error_class", "http_status", "error_code") if row[key] not in (None, "")]
    error = " · ".join(error_parts) or "—"
    cost = "—"
    if row["estimated_cost"] is not None:
        cost = f"{row['estimated_cost']:.8f} {row['cost_currency'] or ''}".strip()
    return (
        "<tr>"
        f"<td title='{escape(str(row['url']))}'>{escape(_truncate(str(row['url']), 72))}</td>"
        f"<td>{escape(str(row['device'] or '—'))}</td>"
        f"<td>{escape(str(row['provider']))}</td>"
        f"<td>{escape(str(row['model'] or '—'))}</td>"
        f"<td>{escape(str(row['reasoning_profile']))}</td>"
        f"<td>{escape(str(row['status']))}</td>"
        f"<td>{_nullable(row['input_tokens'])}</td>"
        f"<td>{_nullable(row['output_tokens'])}</td>"
        f"<td>{_nullable(row['reasoning_tokens'])}</td>"
        f"<td>{escape(cost)}</td>"
        f"<td>{int(row['duration_ms'])} ms</td>"
        f"<td class='m18-error' title='{escape(error)}'>{escape(_truncate(error, 80))}</td>"
        "</tr>"
    )


def _failover_summary(attempts: list[sqlite3.Row]) -> str:
    if not attempts:
        return "NÃO OCORREU"
    by_context: dict[tuple[str, str], list[sqlite3.Row]] = {}
    for row in attempts:
        by_context.setdefault((str(row["url"]), str(row["device"])), []).append(row)
    events: list[str] = []
    for rows in by_context.values():
        if len(rows) < 2:
            continue
        successful = next((row for row in rows if row["status"] == "SUCCESS"), None)
        failed = [row for row in rows if row["status"] != "SUCCESS"]
        if successful and failed:
            first = failed[0]
            events.append(
                f"{escape(str(first['provider']))} ({escape(str(first['error_class'] or first['status']))}) → {escape(str(successful['provider']))}"
            )
    return "; ".join(events) if events else "NÃO OCORREU"


def _provider_label(provider: Any, model: Any) -> str:
    if not provider:
        return ""
    return f"{provider} / {model}" if model else str(provider)


def _nullable(value: Any) -> str:
    return "—" if value is None else escape(str(value))


def _truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return []
    return parsed if isinstance(parsed, list) else []


def _insert_before_body(html: str, block: str) -> str:
    marker = "</body>"
    if marker in html:
        return html.replace(marker, block + marker, 1)
    return html + block
