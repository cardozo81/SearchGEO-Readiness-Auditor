"""Final consistency pass for user-facing report pages.

This module does not collect new data and does not change scoring. It compares
persisted configuration, attempts and observations so the report can explain
when a requested signal was not obtained. It also removes internal milestone
labels from user-facing HTML while preserving internal table/module/event names.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

from searchgeo.persistence import AuditWorkspace
from searchgeo.report_navigation import normalize_report_navigation

_START_INDEX = "<!-- searchgeo-execution-coverage-start -->"
_END_INDEX = "<!-- searchgeo-execution-coverage-end -->"
_START_A11Y = "<!-- searchgeo-accessibility-coverage-start -->"
_END_A11Y = "<!-- searchgeo-accessibility-coverage-end -->"
_START_WEB = "<!-- searchgeo-web-coverage-start -->"
_END_WEB = "<!-- searchgeo-web-coverage-end -->"

_MILESTONE_TEXT_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("M18/M20", "análise semântica e remediação textual"),
    ("M21/M22", "Web Performance e Acessibilidade"),
    ("M21 + M22 · domínio Web Performance", "Domínio Web Performance"),
    ("M23 · domínio Web Performance", "Domínio Synthetic Apdex"),
    ("Web Performance · M23", "Synthetic Apdex"),
    ("M23 · performance sintética transacional", "Performance sintética transacional"),
    ("M23 · metodologia", "Metodologia Synthetic Apdex"),
    ("M22 · domínio independente", "Domínio independente"),
    ("M22 · diagnóstico técnico", "Diagnóstico técnico"),
    ("M22 · fronteiras de domínio", "Fronteiras de domínio"),
    ("M20 · remediação opcional", "Remediação opcional"),
    ("<div class='kicker'>M20</div>", "<div class='kicker'>Remediação textual por IA</div>"),
    ("Estado M23", "Estado"),
    ("Synthetic Apdex M23", "Synthetic Apdex"),
    ("M23 não chama", "Synthetic Apdex não chama"),
    ("regras conservadoras do M23", "regras conservadoras do Synthetic Apdex"),
    ("M20 é projeção auxiliar", "A remediação textual é uma projeção auxiliar"),
    ("Nenhuma chamada M20.", "Nenhuma chamada de remediação textual."),
    ("análise semântica M18", "análise semântica principal"),
    ("pelo M21", "pela coleta de Web Performance"),
    ("M22 Acessibilidade", "Acessibilidade automatizada"),
    ("M21/M23", "Web Performance/Synthetic Apdex"),
)


@dataclass(frozen=True, slots=True)
class CoverageRow:
    component: str
    requested: str
    status: str
    reason: str


@dataclass(frozen=True, slots=True)
class WebContextCoverage:
    url: str
    device: str
    pagespeed_status: str
    pagespeed_http: str
    pagespeed_error: str
    artifact: str
    accessibility_status: str
    accessibility_reason: str
    crux_status: str
    crux_reason: str


def reconcile_report_outputs(*, audit_id: str, workspace: AuditWorkspace) -> None:
    """Reconcile report wording and collection coverage without changing evidence."""
    report_dir = workspace.root / "report"
    if not report_dir.is_dir():
        return

    coverage = _load_execution_coverage(audit_id, workspace)
    contexts = _load_web_context_coverage(audit_id, workspace)

    index_path = report_dir / "index.html"
    if index_path.is_file():
        html = index_path.read_text(encoding="utf-8")
        html = _replace_or_insert(html, _START_INDEX, _END_INDEX, _execution_coverage_section(coverage), "</main>")
        index_path.write_text(_sanitize_public_html(html), encoding="utf-8", newline="\n")

    accessibility_path = report_dir / "accessibility.html"
    if accessibility_path.is_file():
        html = accessibility_path.read_text(encoding="utf-8")
        section = _accessibility_coverage_section(contexts)
        anchor = "<section class='panel'><div class='kicker'>Fronteira de domínio</div>"
        html = _replace_or_insert(html, _START_A11Y, _END_A11Y, section, anchor)
        accessibility_path.write_text(_sanitize_public_html(html), encoding="utf-8", newline="\n")

    web_path = report_dir / "web-performance.html"
    if web_path.is_file():
        html = web_path.read_text(encoding="utf-8")
        html = _remove_apdex_from_web_performance(html)
        section = _web_coverage_section(coverage, contexts)
        anchor = "<section class='panel'><div class='kicker'>Separação metodológica</div>"
        html = _replace_or_insert(html, _START_WEB, _END_WEB, section, anchor)
        web_path.write_text(_sanitize_public_html(html), encoding="utf-8", newline="\n")

    for html_path in report_dir.glob("*.html"):
        if html_path.name in {"index.html", "accessibility.html", "web-performance.html"}:
            continue
        try:
            html = html_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        html_path.write_text(_sanitize_public_html(html), encoding="utf-8", newline="\n")

    normalize_report_navigation(report_dir)


def _table_exists(connection: sqlite3.Connection, table: str) -> bool:
    return connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone() is not None


def _row(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> sqlite3.Row | None:
    try:
        return connection.execute(sql, params).fetchone()
    except sqlite3.OperationalError:
        return None


def _rows(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
    try:
        return list(connection.execute(sql, params).fetchall())
    except sqlite3.OperationalError:
        return []


def _load_execution_coverage(audit_id: str, workspace: AuditWorkspace) -> tuple[CoverageRow, ...]:
    connection = sqlite3.connect(workspace.database)
    connection.row_factory = sqlite3.Row
    try:
        rows: list[CoverageRow] = []

        ai = _row(connection, "SELECT * FROM ai_audit_sessions WHERE audit_id=?", (audit_id,))
        if ai is None:
            rows.append(CoverageRow("Análise semântica por IA", "Não materializada", "NÃO DISPONÍVEL", "Não há sessão de IA persistida para esta auditoria."))
        else:
            enabled = bool(ai["enabled"])
            status = str(ai["status"])
            reason = (
                "IA desabilitada por configuração."
                if not enabled
                else "Resultado semântico válido obtido."
                if status in {"SUCCESS", "PARTIAL"} and ai["effective_provider"]
                else "Provider configurado, mas nenhum resultado semântico válido foi materializado; consulte ai-usage.html."
            )
            rows.append(CoverageRow("Análise semântica por IA", "Sim" if enabled else "Não", status, reason))

        remediation = _row(connection, "SELECT * FROM content_remediation_runs WHERE audit_id=?", (audit_id,))
        if remediation is not None:
            enabled = bool(remediation["enabled"])
            status = str(remediation["status"])
            reason = (
                "Remediação textual por IA desabilitada por configuração."
                if not enabled
                else "Sugestões textuais processadas conforme findings elegíveis."
                if status in {"SUCCESS", "PARTIAL", "NO_ELIGIBLE_FINDINGS"}
                else "A finalidade foi habilitada, mas não concluiu normalmente; consulte Conteúdo/JSON-LD e Uso de IA."
            )
            rows.append(CoverageRow("Remediação textual por IA", "Sim" if enabled else "Não", status, reason))

        web = _row(connection, "SELECT * FROM web_performance_runs WHERE audit_id=?", (audit_id,))
        if web is None:
            rows.append(CoverageRow("Web Performance externo", "Não materializado", "NÃO DISPONÍVEL", "Não há estado de coleta PageSpeed/CrUX persistido."))
        else:
            enabled = bool(web["enabled"])
            status = str(web["status"])
            reason = str(web["reason"] or "")
            if not enabled:
                reason = "Coleta PageSpeed/CrUX desabilitada por configuração."
            elif status == "SUCCESS":
                reason = "Todos os contextos configurados obtiveram evidência de laboratório ou campo."
            elif not reason:
                reason = "Uma ou mais fontes externas não produziram evidência utilizável; consulte as tentativas da página Web Performance."
            rows.append(CoverageRow("Web Performance externo", "Sim" if enabled else "Não", status, reason))

        a11y = _accessibility_summary(connection, audit_id)
        rows.append(a11y)

        apdex = _row(connection, "SELECT * FROM synthetic_apdex_runs WHERE audit_id=?", (audit_id,))
        if apdex is not None:
            enabled = bool(apdex["enabled"])
            status = str(apdex["status"])
            valid = int(apdex["valid_samples"] or 0)
            attempted = int(apdex["attempted_samples"] or 0)
            reason = (
                "Synthetic Apdex desabilitado por configuração."
                if not enabled
                else f"{valid} amostra(s) válida(s) em {attempted} tentativa(s); consulte apdex.html para exclusões e grupos pequenos."
            )
            rows.append(CoverageRow("Synthetic Apdex", "Sim" if enabled else "Não", status, reason))

        return tuple(rows)
    finally:
        connection.close()


def _accessibility_summary(connection: sqlite3.Connection, audit_id: str) -> CoverageRow:
    run = _row(connection, "SELECT * FROM web_performance_runs WHERE audit_id=?", (audit_id,))
    if run is None or not bool(run["enabled"]):
        return CoverageRow("Acessibilidade automatizada", "Não", "NÃO COLETADA", "Depende do payload Lighthouse da coleta Web Performance, que não foi habilitada/materializada.")
    categories = _json_list(run["categories"])
    if "accessibility" not in categories:
        return CoverageRow("Acessibilidade automatizada", "Não", "NÃO SOLICITADA", "A categoria accessibility não foi incluída nas categorias Lighthouse configuradas.")
    observations = _rows(connection, "SELECT accessibility_score,pagespeed_artifact_reference,error_summary FROM web_performance_observations WHERE audit_id=?", (audit_id,))
    if not observations:
        return CoverageRow("Acessibilidade automatizada", "Sim", "NÃO OBTIDA", "Nenhuma observação PageSpeed/Lighthouse foi persistida para os contextos auditados.")
    obtained = sum(row["accessibility_score"] is not None and row["pagespeed_artifact_reference"] for row in observations)
    if obtained == len(observations):
        return CoverageRow("Acessibilidade automatizada", "Sim", "OBTIDA", f"Score/categoria Lighthouse de acessibilidade disponível em {obtained}/{len(observations)} contexto(s).")
    errors = sorted({str(row["error_summary"]) for row in observations if row["error_summary"]})
    detail = "; ".join(errors[:3]) or "PageSpeed/Lighthouse não forneceu artifact/categoria de acessibilidade em todos os contextos."
    return CoverageRow("Acessibilidade automatizada", "Sim", "PARCIAL" if obtained else "NÃO OBTIDA", f"Disponível em {obtained}/{len(observations)} contexto(s). {detail}")


def _load_web_context_coverage(audit_id: str, workspace: AuditWorkspace) -> tuple[WebContextCoverage, ...]:
    connection = sqlite3.connect(workspace.database)
    connection.row_factory = sqlite3.Row
    try:
        run = _row(connection, "SELECT * FROM web_performance_runs WHERE audit_id=?", (audit_id,))
        categories = _json_list(run["categories"]) if run is not None else []
        observations = _rows(
            connection,
            """
            SELECT o.*,p.normalized_url
            FROM web_performance_observations o JOIN pages p ON p.page_id=o.page_id
            WHERE o.audit_id=? ORDER BY p.normalized_url,o.device,o.observation_id
            """,
            (audit_id,),
        )
        attempts = _rows(
            connection,
            "SELECT * FROM web_performance_attempts WHERE audit_id=? ORDER BY created_at,attempt_id",
            (audit_id,),
        )
        by_key: dict[tuple[str, str, str], sqlite3.Row] = {}
        for attempt in attempts:
            key = (str(attempt["page_id"]), str(attempt["snapshot_id"]), str(attempt["service"]).upper())
            by_key[key] = attempt

        result: list[WebContextCoverage] = []
        for observation in observations:
            page_id = str(observation["page_id"])
            snapshot_id = str(observation["snapshot_id"])
            psi = by_key.get((page_id, snapshot_id, "PAGESPEED_INSIGHTS"))
            crux = by_key.get((page_id, snapshot_id, "CRUX_API"))
            psi_status = str(psi["status"]) if psi is not None else "NÃO EXECUTADO"
            psi_http = str(psi["http_status"]) if psi is not None and psi["http_status"] is not None else "—"
            psi_error = _attempt_reason(psi)
            artifact = str(observation["pagespeed_artifact_reference"] or "—")

            if "accessibility" not in categories:
                a11y_status = "NÃO SOLICITADA"
                a11y_reason = "Categoria accessibility ausente da configuração Lighthouse."
            elif psi is None:
                a11y_status = "NÃO OBTIDA"
                a11y_reason = "Não houve tentativa PageSpeed/Lighthouse persistida para este contexto."
            elif psi_status != "SUCCESS":
                a11y_status = "NÃO OBTIDA"
                a11y_reason = f"PageSpeed/Lighthouse falhou: {psi_error}."
            elif not observation["pagespeed_artifact_reference"]:
                a11y_status = "NÃO OBTIDA"
                a11y_reason = "A chamada PageSpeed terminou, mas não houve artifact Lighthouse persistido."
            elif observation["accessibility_score"] is None:
                a11y_status = "NÃO OBTIDA"
                a11y_reason = "Artifact Lighthouse persistido, porém a categoria/score accessibility não foi fornecida pela fonte."
            else:
                a11y_status = "OBTIDA"
                a11y_reason = f"Lighthouse accessibility score {float(observation['accessibility_score']):.0f}/100 persistido."

            if crux is None:
                crux_status = "NÃO EXECUTADO"
                field_source = str(observation["field_source"] or "")
                crux_reason = "Dados de campo vieram da resposta PageSpeed." if field_source == "PAGESPEED_CRUX" else "CrUX direto não foi necessário/configurado ou não havia credencial elegível."
            else:
                crux_status = str(crux["status"])
                crux_reason = _attempt_reason(crux)

            result.append(
                WebContextCoverage(
                    url=str(observation["normalized_url"]),
                    device=str(observation["device"]),
                    pagespeed_status=psi_status,
                    pagespeed_http=psi_http,
                    pagespeed_error=psi_error,
                    artifact=artifact,
                    accessibility_status=a11y_status,
                    accessibility_reason=a11y_reason,
                    crux_status=crux_status,
                    crux_reason=crux_reason,
                )
            )
        return tuple(result)
    finally:
        connection.close()


def _attempt_reason(row: sqlite3.Row | None) -> str:
    if row is None:
        return "sem tentativa persistida"
    parts: list[str] = []
    if row["http_status"] is not None:
        parts.append(f"HTTP {row['http_status']}")
    if row["error_code"]:
        parts.append(str(row["error_code"]))
    if row["error_message"]:
        parts.append(str(row["error_message"]))
    if not parts and str(row["status"]) == "SUCCESS":
        return "sucesso"
    return " · ".join(parts) or str(row["status"])


def _execution_coverage_section(rows: tuple[CoverageRow, ...]) -> str:
    body = "".join(
        "<tr>"
        f"<td>{escape(row.component)}</td><td>{escape(row.requested)}</td>"
        f"<td><strong>{escape(row.status)}</strong></td><td>{escape(row.reason)}</td>"
        "</tr>"
        for row in rows
    )
    return (
        f"{_START_INDEX}<section id='execution-coverage' class='panel'>"
        "<div class='kicker'>Rastreabilidade da execução</div><h2>Configuração × resultado obtido</h2>"
        "<p class='intro'>Esta seção compara o que foi habilitado com o que realmente foi materializado. "
        "Falha de API, quota, timeout, ausência de amostra ou dado não fornecido pela fonte é registrada como limitação da coleta; não é convertida silenciosamente em resultado do site.</p>"
        "<div class='table-wrap'><table><thead><tr><th>Componente</th><th>Solicitado</th><th>Resultado</th><th>Motivo / evidência</th></tr></thead>"
        f"<tbody>{body or '<tr><td colspan="4">Nenhum estado complementar materializado.</td></tr>'}</tbody></table></div></section>{_END_INDEX}"
    )


def _accessibility_coverage_section(contexts: tuple[WebContextCoverage, ...]) -> str:
    rows = "".join(
        "<tr>"
        f"<td class='mono'>{escape(item.url)}</td><td>{escape(item.device.upper())}</td>"
        f"<td><strong>{escape(item.accessibility_status)}</strong></td>"
        f"<td>{escape(item.accessibility_reason)}</td>"
        f"<td>{escape(item.pagespeed_status)} / HTTP {escape(item.pagespeed_http)}</td>"
        f"<td><code>{escape(item.artifact)}</code></td>"
        "</tr>"
        for item in contexts
    )
    if not rows:
        rows = '<tr><td colspan="6">Nenhum contexto Web Performance foi materializado; não há evidência Lighthouse de acessibilidade para projetar.</td></tr>'
    return (
        f"{_START_A11Y}<section id='accessibility-collection-coverage' class='panel'>"
        "<div class='kicker'>Cobertura da coleta</div><h2>Por que a acessibilidade pode estar indisponível</h2>"
        "<p class='intro'>A auditoria automatizada de acessibilidade usa a categoria <code>accessibility</code> do mesmo payload Lighthouse obtido via PageSpeed. "
        "Se essa chamada falha, é interrompida, excede quota ou retorna payload sem a categoria, esta página informa a causa em vez de assumir score ou ausência de falhas.</p>"
        "<div class='table-wrap'><table><thead><tr><th>URL</th><th>Device</th><th>Acessibilidade</th><th>Motivo</th><th>PageSpeed</th><th>Artifact</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div></section>{_END_A11Y}"
    )


def _web_coverage_section(coverage: tuple[CoverageRow, ...], contexts: tuple[WebContextCoverage, ...]) -> str:
    web = next((row for row in coverage if row.component == "Web Performance externo"), None)
    summary = escape(web.reason if web else "Estado de Web Performance não materializado.")
    rows = "".join(
        "<tr>"
        f"<td class='mono'>{escape(item.url)}</td><td>{escape(item.device.upper())}</td>"
        f"<td>{escape(item.pagespeed_status)}</td><td>{escape(item.pagespeed_http)}</td>"
        f"<td>{escape(item.pagespeed_error)}</td><td>{escape(item.crux_status)}</td><td>{escape(item.crux_reason)}</td>"
        "</tr>"
        for item in contexts
    )
    if not rows:
        rows = '<tr><td colspan="7">Nenhuma tentativa externa materializada para os contextos auditados.</td></tr>'
    return (
        f"{_START_WEB}<section id='web-collection-coverage' class='panel'>"
        "<div class='kicker'>Cobertura da coleta</div><h2>Configuração, chamadas e limitações</h2>"
        f"<p class='intro'>{summary}</p>"
        "<p class='intro'>Valores ausentes permanecem como indisponíveis. HTTP 4xx/5xx, quota, timeout e ausência de amostra CrUX são limitações da fonte/coleta e não são substituídos por valores de outra métrica.</p>"
        "<div class='table-wrap'><table><thead><tr><th>URL</th><th>Device</th><th>PageSpeed</th><th>HTTP</th><th>Erro/limitação</th><th>CrUX direto</th><th>Motivo CrUX</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div></section>{_END_WEB}"
    )


def _remove_apdex_from_web_performance(html: str) -> str:
    # The Apdex domain owns its own page. Web Performance keeps only the nav link.
    html = re.sub(
        r"<!-- searchgeo-m23-web-start -->.*?<!-- searchgeo-m23-web-end -->",
        "",
        html,
        count=1,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<div class='metric'><small>Apdex</small><strong>NÃO CALCULADO</strong></div>",
        "",
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"<div class='notice warn'><strong>Apdex não é inferido de Lighthouse/CrUX\.</strong>.*?</div>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html = re.sub(
        r"<li><a href='[^']*apdex[^']*'[^>]*>Apdex Technical Specification v1\.1</a>.*?</li>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return html


def _sanitize_public_html(html: str) -> str:
    for old, new in _MILESTONE_TEXT_REPLACEMENTS:
        html = html.replace(old, new)
    # Internal lowercase ids/classes/comments remain untouched. Remaining uppercase
    # milestone tokens are presentation residue and have no user-facing meaning.
    html = re.sub(r"\bM(?:7|11|14|15|16|17|18|20|21|22|23)\b\s*[·+\-/]*\s*", "", html)
    html = re.sub(r"\s{2,}", " ", html)
    return html


def _json_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).casefold() for item in value]
    if not value:
        return []
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return []
    return [str(item).casefold() for item in parsed] if isinstance(parsed, list) else []


def _replace_or_insert(html: str, start: str, end: str, content: str, before: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), flags=re.DOTALL)
    if pattern.search(html):
        return pattern.sub(content, html, count=1)
    return html.replace(before, content + before, 1) if before in html else html + content
