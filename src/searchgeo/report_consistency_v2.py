"""User-facing report consistency and collection-coverage projection.

This pass never collects new data or changes scoring. It explains when requested
signals were not obtained and removes internal milestone labels from public HTML.
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


@dataclass(frozen=True, slots=True)
class Coverage:
    component: str
    requested: str
    status: str
    reason: str


@dataclass(frozen=True, slots=True)
class Context:
    url: str
    device: str
    psi_status: str
    psi_http: str
    psi_reason: str
    artifact: str
    a11y_status: str
    a11y_reason: str
    crux_status: str
    crux_reason: str


_TEXT_REPLACEMENTS = (
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
    ("Estado M23", "Estado"),
    ("Synthetic Apdex M23", "Synthetic Apdex"),
    ("M23 não chama", "Synthetic Apdex não chama"),
    ("regras conservadoras do M23", "regras conservadoras do Synthetic Apdex"),
    ("M20 é projeção auxiliar", "A remediação textual é uma projeção auxiliar"),
    ("Nenhuma chamada M20.", "Nenhuma chamada de remediação textual."),
    ("análise semântica M18", "análise semântica principal"),
    ("pelo M21", "pela coleta de Web Performance"),
    ("M22 Acessibilidade", "Acessibilidade automatizada"),
)
_MILESTONE = re.compile(r"\bM(?:7|11|14|15|16|17|18|20|21|22|23)\b\s*[·+\-/]*\s*")


def reconcile_report_outputs(*, audit_id: str, workspace: AuditWorkspace) -> None:
    report_dir = workspace.root / "report"
    if not report_dir.is_dir():
        return
    coverage = _coverage(audit_id, workspace)
    contexts = _contexts(audit_id, workspace)

    index = report_dir / "index.html"
    if index.is_file():
        html = _replace(index.read_text(encoding="utf-8"), "execution-coverage", _coverage_html(coverage), "</main>")
        index.write_text(_sanitize(html), encoding="utf-8", newline="\n")

    a11y = report_dir / "accessibility.html"
    if a11y.is_file():
        html = _replace(a11y.read_text(encoding="utf-8"), "accessibility-coverage", _a11y_html(contexts), "<section class='panel'><div class='kicker'>Fronteira de domínio</div>")
        a11y.write_text(_sanitize(html), encoding="utf-8", newline="\n")

    web = report_dir / "web-performance.html"
    if web.is_file():
        html = _strip_apdex_from_web(web.read_text(encoding="utf-8"))
        html = _replace(html, "web-coverage", _web_html(coverage, contexts), "<section class='panel'><div class='kicker'>Separação metodológica</div>")
        web.write_text(_sanitize(html), encoding="utf-8", newline="\n")

    for path in report_dir.glob("*.html"):
        if path.name in {"index.html", "accessibility.html", "web-performance.html"}:
            continue
        try:
            html = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        path.write_text(_sanitize(html), encoding="utf-8", newline="\n")
    normalize_report_navigation(report_dir)


def _one(db: sqlite3.Connection, sql: str, audit_id: str) -> sqlite3.Row | None:
    try:
        return db.execute(sql, (audit_id,)).fetchone()
    except sqlite3.OperationalError:
        return None


def _many(db: sqlite3.Connection, sql: str, audit_id: str) -> list[sqlite3.Row]:
    try:
        return list(db.execute(sql, (audit_id,)).fetchall())
    except sqlite3.OperationalError:
        return []


def _coverage(audit_id: str, workspace: AuditWorkspace) -> tuple[Coverage, ...]:
    db = sqlite3.connect(workspace.database)
    db.row_factory = sqlite3.Row
    try:
        result: list[Coverage] = []
        ai = _one(db, "SELECT * FROM ai_audit_sessions WHERE audit_id=?", audit_id)
        if ai is not None:
            enabled = bool(ai["enabled"])
            result.append(Coverage(
                "Análise semântica por IA", "Sim" if enabled else "Não", str(ai["status"]),
                "IA desabilitada por configuração." if not enabled else (
                    "Resultado semântico válido obtido." if ai["effective_provider"] else
                    "Nenhum resultado semântico válido foi materializado; consulte Uso de IA."
                ),
            ))
        remediation = _one(db, "SELECT * FROM content_remediation_runs WHERE audit_id=?", audit_id)
        if remediation is not None:
            enabled, status = bool(remediation["enabled"]), str(remediation["status"])
            result.append(Coverage(
                "Remediação textual por IA", "Sim" if enabled else "Não", status,
                "Remediação textual desabilitada por configuração." if not enabled else (
                    "Finalidade processada conforme findings elegíveis." if status in {"SUCCESS", "PARTIAL", "NO_ELIGIBLE_FINDINGS"} else
                    "A finalidade foi habilitada, mas não concluiu normalmente; consulte Conteúdo/JSON-LD e Uso de IA."
                ),
            ))
        web = _one(db, "SELECT * FROM web_performance_runs WHERE audit_id=?", audit_id)
        if web is not None:
            enabled, status = bool(web["enabled"]), str(web["status"])
            reason = "Coleta PageSpeed/CrUX desabilitada por configuração." if not enabled else (
                "Todos os contextos configurados obtiveram evidência utilizável." if status == "SUCCESS" else
                str(web["reason"] or "Uma ou mais fontes não produziram evidência utilizável; consulte as tentativas de Web Performance.")
            )
            result.append(Coverage("Web Performance externo", "Sim" if enabled else "Não", status, reason))
        result.append(_a11y_coverage(db, audit_id))
        apdex = _one(db, "SELECT * FROM synthetic_apdex_runs WHERE audit_id=?", audit_id)
        if apdex is not None:
            enabled, status = bool(apdex["enabled"]), str(apdex["status"])
            valid, attempted = int(apdex["valid_samples"] or 0), int(apdex["attempted_samples"] or 0)
            reason = "Synthetic Apdex desabilitado por configuração." if not enabled else f"{valid} amostra(s) válida(s) em {attempted} tentativa(s); consulte Apdex para exclusões e grupos pequenos."
            result.append(Coverage("Synthetic Apdex", "Sim" if enabled else "Não", status, reason))
        return tuple(result)
    finally:
        db.close()


def _a11y_coverage(db: sqlite3.Connection, audit_id: str) -> Coverage:
    run = _one(db, "SELECT * FROM web_performance_runs WHERE audit_id=?", audit_id)
    if run is None or not bool(run["enabled"]):
        return Coverage("Acessibilidade automatizada", "Não", "NÃO COLETADA", "Depende do payload Lighthouse da coleta Web Performance, que não foi habilitada/materializada.")
    categories = _json_list(run["categories"])
    if "accessibility" not in categories:
        return Coverage("Acessibilidade automatizada", "Não", "NÃO SOLICITADA", "A categoria accessibility não foi incluída na configuração Lighthouse.")
    observations = _many(db, "SELECT accessibility_score,pagespeed_artifact_reference,error_summary FROM web_performance_observations WHERE audit_id=?", audit_id)
    if not observations:
        return Coverage("Acessibilidade automatizada", "Sim", "NÃO OBTIDA", "Nenhuma observação PageSpeed/Lighthouse foi persistida.")
    obtained = sum(row["accessibility_score"] is not None and row["pagespeed_artifact_reference"] for row in observations)
    if obtained == len(observations):
        return Coverage("Acessibilidade automatizada", "Sim", "OBTIDA", f"Categoria/score Lighthouse disponível em {obtained}/{len(observations)} contexto(s).")
    errors = sorted({str(row["error_summary"]) for row in observations if row["error_summary"]})
    reason = "; ".join(errors[:3]) or "PageSpeed/Lighthouse não forneceu artifact/categoria de acessibilidade em todos os contextos."
    return Coverage("Acessibilidade automatizada", "Sim", "PARCIAL" if obtained else "NÃO OBTIDA", f"Disponível em {obtained}/{len(observations)} contexto(s). {reason}")


def _contexts(audit_id: str, workspace: AuditWorkspace) -> tuple[Context, ...]:
    db = sqlite3.connect(workspace.database)
    db.row_factory = sqlite3.Row
    try:
        run = _one(db, "SELECT * FROM web_performance_runs WHERE audit_id=?", audit_id)
        categories = _json_list(run["categories"]) if run is not None else []
        observations = _many(db, """SELECT o.*,p.normalized_url FROM web_performance_observations o JOIN pages p ON p.page_id=o.page_id WHERE o.audit_id=? ORDER BY p.normalized_url,o.device,o.observation_id""", audit_id)
        attempts = _many(db, "SELECT * FROM web_performance_attempts WHERE audit_id=? ORDER BY created_at,attempt_id", audit_id)
        by_key = {(str(r["page_id"]), str(r["snapshot_id"]), str(r["service"]).upper()): r for r in attempts}
        output: list[Context] = []
        for o in observations:
            base = (str(o["page_id"]), str(o["snapshot_id"]))
            psi, crux = by_key.get((*base, "PAGESPEED_INSIGHTS")), by_key.get((*base, "CRUX_API"))
            psi_status = str(psi["status"]) if psi is not None else "NÃO EXECUTADO"
            psi_http = str(psi["http_status"]) if psi is not None and psi["http_status"] is not None else "—"
            psi_reason = _attempt_reason(psi)
            artifact = str(o["pagespeed_artifact_reference"] or "—")
            if "accessibility" not in categories:
                a11y_status, a11y_reason = "NÃO SOLICITADA", "Categoria accessibility ausente da configuração Lighthouse."
            elif psi is None:
                a11y_status, a11y_reason = "NÃO OBTIDA", "Não houve tentativa PageSpeed/Lighthouse persistida."
            elif psi_status != "SUCCESS":
                a11y_status, a11y_reason = "NÃO OBTIDA", f"PageSpeed/Lighthouse falhou: {psi_reason}."
            elif not o["pagespeed_artifact_reference"]:
                a11y_status, a11y_reason = "NÃO OBTIDA", "A chamada terminou sem artifact Lighthouse persistido."
            elif o["accessibility_score"] is None:
                a11y_status, a11y_reason = "NÃO OBTIDA", "Artifact persistido, porém categoria/score accessibility ausente na fonte."
            else:
                a11y_status, a11y_reason = "OBTIDA", f"Lighthouse accessibility score {float(o['accessibility_score']):.0f}/100 persistido."
            if crux is None:
                crux_status = "NÃO EXECUTADO"
                crux_reason = "Dados de campo vieram do PageSpeed." if str(o["field_source"] or "") == "PAGESPEED_CRUX" else "CrUX direto não foi necessário/configurado ou não havia credencial elegível."
            else:
                crux_status, crux_reason = str(crux["status"]), _attempt_reason(crux)
            output.append(Context(str(o["normalized_url"]), str(o["device"]), psi_status, psi_http, psi_reason, artifact, a11y_status, a11y_reason, crux_status, crux_reason))
        return tuple(output)
    finally:
        db.close()


def _attempt_reason(row: sqlite3.Row | None) -> str:
    if row is None:
        return "sem tentativa persistida"
    parts = []
    if row["http_status"] is not None: parts.append(f"HTTP {row['http_status']}")
    if row["error_code"]: parts.append(str(row["error_code"]))
    if row["error_message"]: parts.append(str(row["error_message"]))
    return "sucesso" if not parts and str(row["status"]) == "SUCCESS" else (" · ".join(parts) or str(row["status"]))


def _coverage_html(rows: tuple[Coverage, ...]) -> str:
    body = "".join(f"<tr><td>{escape(r.component)}</td><td>{escape(r.requested)}</td><td><strong>{escape(r.status)}</strong></td><td>{escape(r.reason)}</td></tr>" for r in rows)
    return f"""<section id='execution-coverage' class='panel'><div class='kicker'>Rastreabilidade da execução</div><h2>Configuração × resultado obtido</h2><p class='intro'>Compara o que foi habilitado com o que realmente foi materializado. Falha de API, quota, timeout, ausência de amostra ou dado não fornecido pela fonte permanece como limitação da coleta; não é convertido silenciosamente em resultado do site.</p><div class='table-wrap'><table><thead><tr><th>Componente</th><th>Solicitado</th><th>Resultado</th><th>Motivo / evidência</th></tr></thead><tbody>{body or '<tr><td colspan="4">Nenhum estado complementar materializado.</td></tr>'}</tbody></table></div></section>"""


def _a11y_html(contexts: tuple[Context, ...]) -> str:
    body = "".join(f"<tr><td class='mono'>{escape(c.url)}</td><td>{escape(c.device.upper())}</td><td><strong>{escape(c.a11y_status)}</strong></td><td>{escape(c.a11y_reason)}</td><td>{escape(c.psi_status)} / HTTP {escape(c.psi_http)}</td><td><code>{escape(c.artifact)}</code></td></tr>" for c in contexts) or '<tr><td colspan="6">Nenhum contexto Web Performance materializado; não há evidência Lighthouse de acessibilidade para projetar.</td></tr>'
    return f"""<section id='accessibility-coverage' class='panel'><div class='kicker'>Cobertura da coleta</div><h2>Por que a acessibilidade pode estar indisponível</h2><p class='intro'>A auditoria automatizada usa a categoria <code>accessibility</code> do payload Lighthouse obtido via PageSpeed. Falha, interrupção, quota ou payload sem a categoria são exibidos como causa; ausência de dado nunca é tratada como ausência de problema.</p><div class='table-wrap'><table><thead><tr><th>URL</th><th>Device</th><th>Acessibilidade</th><th>Motivo</th><th>PageSpeed</th><th>Artifact</th></tr></thead><tbody>{body}</tbody></table></div></section>"""


def _web_html(coverage: tuple[Coverage, ...], contexts: tuple[Context, ...]) -> str:
    web = next((r for r in coverage if r.component == "Web Performance externo"), None)
    body = "".join(f"<tr><td class='mono'>{escape(c.url)}</td><td>{escape(c.device.upper())}</td><td>{escape(c.psi_status)}</td><td>{escape(c.psi_http)}</td><td>{escape(c.psi_reason)}</td><td>{escape(c.crux_status)}</td><td>{escape(c.crux_reason)}</td></tr>" for c in contexts) or '<tr><td colspan="7">Nenhuma tentativa externa materializada.</td></tr>'
    return f"""<section id='web-coverage' class='panel'><div class='kicker'>Cobertura da coleta</div><h2>Configuração, chamadas e limitações</h2><p class='intro'>{escape(web.reason if web else 'Estado de Web Performance não materializado.')}</p><p class='intro'>Valores ausentes permanecem indisponíveis. HTTP 4xx/5xx, quota, timeout e ausência de amostra CrUX não são substituídos por valores de outra métrica.</p><div class='table-wrap'><table><thead><tr><th>URL</th><th>Device</th><th>PageSpeed</th><th>HTTP</th><th>Erro/limitação</th><th>CrUX direto</th><th>Motivo CrUX</th></tr></thead><tbody>{body}</tbody></table></div></section>"""


def _strip_apdex_from_web(html: str) -> str:
    html = re.sub(r"<!-- searchgeo-m23-web-start -->.*?<!-- searchgeo-m23-web-end -->", "", html, count=1, flags=re.DOTALL)
    html = re.sub(r"<div class='metric'><small>Apdex</small><strong>NÃO CALCULADO</strong></div>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<div class='notice warn'><strong>Apdex não é inferido de Lighthouse/CrUX\.</strong>.*?</div>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<li><a href='[^']*apdex[^']*'[^>]*>Apdex Technical Specification v1\.1</a>.*?</li>", "", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def _sanitize(html: str) -> str:
    for old, new in _TEXT_REPLACEMENTS:
        html = html.replace(old, new)
    parts = re.split(r"(<[^>]+>)", html)
    for i in range(0, len(parts), 2):
        parts[i] = _MILESTONE.sub("", parts[i])
    return "".join(parts)


def _replace(html: str, section_id: str, content: str, before: str) -> str:
    pattern = re.compile(rf"<section id=['\"]{re.escape(section_id)}['\"].*?</section>", flags=re.DOTALL)
    if pattern.search(html):
        return pattern.sub(content, html, count=1)
    return html.replace(before, content + before, 1) if before in html else html + content


def _json_list(value: Any) -> list[str]:
    if isinstance(value, list): return [str(x).casefold() for x in value]
    if not value: return []
    try: parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError): return []
    return [str(x).casefold() for x in parsed] if isinstance(parsed, list) else []
