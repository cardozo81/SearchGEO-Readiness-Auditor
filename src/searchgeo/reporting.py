"""M11 static, self-contained HTML reporting from persisted audit data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

from searchgeo.domain import AuditMode, new_id, utc_now
from searchgeo.persistence import AuditWorkspace


TEMPLATE_VERSION = "REPORT-GEO-001"

_DIMENSION_LABELS = {
    "TECHNICAL_ACCESSIBILITY": "Acessibilidade Técnica",
    "INDEXABILITY": "Capacidade de Indexação",
    "CONTENT_EXTRACTABILITY": "Extração de Conteúdo",
    "SEMANTIC_STRUCTURE": "Estrutura Semântica",
    "ENTITY_CLARITY": "Clareza de Entidades",
    "STRUCTURED_DATA": "Dados Estruturados",
    "ANSWERABILITY": "Capacidade de Resposta",
    "CITATION_READINESS": "Preparação para Citação",
    "EVIDENCE_TRUST": "Evidências e Confiabilidade",
    "INTENT_COVERAGE": "Cobertura de Intenções",
    "OVERALL_READINESS": "Readiness Geral",
}
_STATUS_LABELS = {
    "PASS": "Aprovado",
    "FAIL": "Problema identificado",
    "WARNING": "Alerta",
    "UNKNOWN": "Não Determinado",
    "NOT_APPLICABLE": "Não aplicável",
    "ERROR": "Erro de execução da análise",
    "CONSOLIDATED": "Consolidado",
    "PARTIAL": "Parcial",
    "NOT_CONSOLIDATED": "Não Consolidado",
    "HIGH": "Alta",
    "MEDIUM": "Média",
    "LOW": "Baixa",
    "UNAVAILABLE": "Indisponível",
}
_PRIORITY_LABELS = {
    "P0": "P0 — blocker crítico",
    "P1": "P1 — prioridade muito alta",
    "P2": "P2 — prioridade alta",
    "P3": "P3 — prioridade média",
    "P4": "P4 — prioridade baixa",
    "INFO": "Informacional",
}
_SENSITIVE_KEY = re.compile(r"(?:api[_-]?key|authorization|password|passwd|secret|access[_-]?token|bearer|credential)", re.I)


@dataclass(frozen=True, slots=True)
class ReportRecord:
    report_id: str
    audit_id: str
    format: str
    status: str
    generated_at: datetime
    template_version: str
    auditor_version: str
    file_path: str


class ReportPersistence:
    """Persist report metadata; the HTML remains a projection, never primary data."""

    def __init__(self, workspace: AuditWorkspace) -> None:
        self._connection = sqlite3.connect(workspace.database)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "ReportPersistence":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def _initialize(self) -> None:
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    audit_id TEXT NOT NULL REFERENCES audits(audit_id) ON DELETE CASCADE,
                    format TEXT NOT NULL,
                    status TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    template_version TEXT NOT NULL,
                    auditor_version TEXT NOT NULL,
                    file_path TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_reports_audit_generated
                    ON reports(audit_id, generated_at DESC);
                """
            )

    def add(self, report: ReportRecord) -> None:
        with self._connection:
            self._connection.execute(
                "INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    report.report_id,
                    report.audit_id,
                    report.format,
                    report.status,
                    report.generated_at.isoformat(),
                    report.template_version,
                    report.auditor_version,
                    report.file_path,
                ),
            )

    def get(self, report_id: str) -> ReportRecord | None:
        row = self._connection.execute(
            "SELECT * FROM reports WHERE report_id = ?", (report_id,)
        ).fetchone()
        if row is None:
            return None
        return ReportRecord(
            report_id=row["report_id"],
            audit_id=row["audit_id"],
            format=row["format"],
            status=row["status"],
            generated_at=datetime.fromisoformat(row["generated_at"]),
            template_version=row["template_version"],
            auditor_version=row["auditor_version"],
            file_path=row["file_path"],
        )


class ReportBuilder:
    """Render one professional HTML5 report using only persisted audit state."""

    def build(self, *, audit_id: str, workspace: AuditWorkspace) -> str:
        connection = sqlite3.connect(workspace.database)
        connection.row_factory = sqlite3.Row
        try:
            audit = connection.execute("SELECT * FROM audits WHERE audit_id = ?", (audit_id,)).fetchone()
            if audit is None:
                raise ValueError(f"audit not found: {audit_id}")
            pages = self._query(connection, "SELECT * FROM pages WHERE audit_id = ? ORDER BY depth, normalized_url", (audit_id,))
            scores = self._query_optional(connection, "SELECT * FROM scores WHERE audit_id = ? ORDER BY device, dimension", (audit_id,))
            findings = self._query(
                connection,
                """
                SELECT * FROM findings WHERE audit_id = ?
                ORDER BY CASE severity WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 WHEN 'LOW' THEN 3 ELSE 4 END,
                         rule_id, finding_id
                """,
                (audit_id,),
            )
            recommendations = self._query_optional(
                connection,
                "SELECT * FROM recommendations WHERE audit_id = ? ORDER BY priority_score DESC, recommendation_id",
                (audit_id,),
            )
            groups = self._query_optional(
                connection,
                "SELECT * FROM remediation_groups WHERE audit_id = ? ORDER BY priority_score DESC, group_id",
                (audit_id,),
            )
            executions = self._query(
                connection,
                "SELECT result, COUNT(*) AS n FROM rule_executions WHERE audit_id = ? GROUP BY result ORDER BY result",
                (audit_id,),
            )
            evidence = self._evidence_for_findings(connection, audit_id=audit_id, findings=findings)
        finally:
            connection.close()

        audit_mode = AuditMode(audit["audit_mode"]) if audit["audit_mode"] else None
        limitations = tuple(_json_list(audit["limitations"]))
        capabilities = tuple(_json_list(audit["capabilities"]))
        score_by_device = self._score_groups(scores)
        group_by_id = {row["group_id"]: row for row in groups}

        body = "".join(
            (
                self._hero(audit=audit, pages=pages, findings=findings, recommendations=recommendations),
                self._interpretation(),
                self._reliability(audit_mode=audit_mode, capabilities=capabilities, limitations=limitations, scores=scores),
                self._scorecards(score_by_device),
                self._findings(findings=findings, evidence=evidence),
                self._recommendations(recommendations=recommendations, groups=group_by_id),
                self._limitations(audit_mode=audit_mode, limitations=limitations),
                self._technical(audit=audit, pages=pages, executions=executions),
                self._glossary(),
            )
        )
        return self._document(title=f"SearchGEO Readiness — {_text(audit['project_name'])}", body=body)

    @staticmethod
    def _query(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
        return list(connection.execute(sql, params).fetchall())

    @staticmethod
    def _query_optional(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
        try:
            return list(connection.execute(sql, params).fetchall())
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc).lower():
                return []
            raise

    @classmethod
    def _evidence_for_findings(
        cls,
        connection: sqlite3.Connection,
        *,
        audit_id: str,
        findings: list[sqlite3.Row],
    ) -> dict[str, sqlite3.Row]:
        ids: list[str] = []
        for finding in findings:
            ids.extend(str(value) for value in _json_list(finding["evidence_ids"]))
        unique = tuple(dict.fromkeys(ids))
        if not unique:
            return {}
        placeholders = ",".join("?" for _ in unique)
        rows = connection.execute(
            f"SELECT * FROM evidence WHERE audit_id = ? AND evidence_id IN ({placeholders}) ORDER BY evidence_id",
            (audit_id, *unique),
        ).fetchall()
        return {row["evidence_id"]: row for row in rows}

    @staticmethod
    def _score_groups(scores: list[sqlite3.Row]) -> dict[str, list[sqlite3.Row]]:
        grouped: dict[str, list[sqlite3.Row]] = {"DESKTOP": [], "MOBILE": []}
        for score in scores:
            grouped.setdefault(score["device"], []).append(score)
        return grouped

    def _hero(
        self,
        *,
        audit: sqlite3.Row,
        pages: list[sqlite3.Row],
        findings: list[sqlite3.Row],
        recommendations: list[sqlite3.Row],
    ) -> str:
        return f"""
        <header class="hero">
          <div class="eyebrow">SearchGEO Readiness Auditor</div>
          <h1>Relatório de readiness para busca e sistemas generativos</h1>
          <p class="lead">Avaliação técnica e semântica rastreável. O relatório mede readiness; não promete ranking, citação, visibilidade ou presença em mecanismos generativos.</p>
          <div class="meta-grid">
            {_metric("Projeto", audit['project_name'])}
            {_metric("Auditoria", audit['audit_id'])}
            {_metric("Páginas auditadas", len(pages))}
            {_metric("Problemas identificados", len(findings))}
            {_metric("Recomendações", len(recommendations))}
            {_metric("Idioma / mercado", f"{audit['primary_language']} / {audit['market']}")}
          </div>
        </header>
        """

    @staticmethod
    def _interpretation() -> str:
        items = (
            ("Nota", "Resultado quantitativo das regras efetivamente avaliadas."),
            ("Cobertura da Análise", "Quanto do universo aplicável pôde ser efetivamente analisado. Baixa cobertura não significa necessariamente baixa qualidade do site."),
            ("Confiabilidade", "Grau de segurança da conclusão com base em evidências, método, cobertura e limitações."),
            ("Consolidado", "Há cobertura e confiabilidade suficientes para apresentar o resultado como consolidado."),
            ("Parcial", "Parte relevante da avaliação está disponível, mas existem limitações."),
            ("Não Consolidado", "Não há base suficiente para apresentar uma nota conclusiva."),
            ("Severidade", "Gravidade intrínseca do problema identificado."),
            ("Prioridade", "Ordem recomendada de ação considerando gravidade, impacto, confiabilidade e facilidade."),
            ("Desktop e Mobile", "São contextos independentes e podem apresentar resultados diferentes."),
        )
        cards = "".join(f"<div class='explain'><h3>{escape(title)}</h3><p>{escape(text)}</p></div>" for title, text in items)
        return f"<section><h2>Como interpretar este relatório</h2><div class='explain-grid'>{cards}</div></section>"

    def _reliability(
        self,
        *,
        audit_mode: AuditMode | None,
        capabilities: tuple[str, ...],
        limitations: tuple[str, ...],
        scores: list[sqlite3.Row],
    ) -> str:
        consolidated = sum(1 for row in scores if row["consolidation_status"] == "CONSOLIDATED")
        partial = sum(1 for row in scores if row["consolidation_status"] == "PARTIAL")
        non = sum(1 for row in scores if row["consolidation_status"] == "NOT_CONSOLIDATED")
        ai_note = self._ai_disclaimer(audit_mode=audit_mode, capabilities=capabilities)
        limitation_html = "".join(f"<li>{escape(_text(item))}</li>" for item in limitations) or "<li>Nenhuma limitação adicional foi registrada no objeto Audit.</li>"
        return f"""
        <section>
          <h2>Confiabilidade da auditoria</h2>
          <div class="meta-grid compact">
            {_metric("Modo", audit_mode.value if audit_mode else "Não informado")}
            {_metric("Dimensões consolidadas", consolidated)}
            {_metric("Dimensões parciais", partial)}
            {_metric("Dimensões não consolidadas", non)}
          </div>
          <div class="notice">{escape(ai_note)}</div>
          <h3>Limitações registradas</h3><ul>{limitation_html}</ul>
        </section>
        """

    @staticmethod
    def _ai_disclaimer(*, audit_mode: AuditMode | None, capabilities: tuple[str, ...]) -> str:
        if audit_mode is AuditMode.NO_AI or any("NO_AI" in value.upper() for value in capabilities):
            return (
                "Algumas avaliações semânticas não foram executadas porque não havia um provedor de inteligência artificial disponível ou configurado. "
                "Essa limitação reduz a cobertura da auditoria e não representa um problema do website analisado."
            )
        if audit_mode in {AuditMode.FULL, AuditMode.DEGRADED} and any(
            "OPENAI" in value.upper() or "AI_PROVIDER" in value.upper() for value in capabilities
        ):
            return "Análises semânticas utilizaram um provedor externo de inteligência artificial configurado para a auditoria. Credenciais não são incluídas neste relatório."
        return "A disponibilidade de análise semântica é refletida em cobertura, confiabilidade e limitações; ausência de capacidade não é tratada como defeito do website."

    def _scorecards(self, grouped: dict[str, list[sqlite3.Row]]) -> str:
        blocks = []
        for device in ("DESKTOP", "MOBILE"):
            rows = grouped.get(device, [])
            if not rows:
                blocks.append(f"<article class='device'><h3>{device.title()}</h3><p class='muted'>Nenhum score persistido disponível.</p></article>")
                continue
            body = "".join(self._score_row(row) for row in rows)
            blocks.append(f"<article class='device'><h3>{device.title()}</h3><div class='score-list'>{body}</div></article>")
        return f"<section><h2>Scorecard por dispositivo</h2><div class='devices'>{''.join(blocks)}</div></section>"

    @staticmethod
    def _score_row(row: sqlite3.Row) -> str:
        dimension = _DIMENSION_LABELS.get(row["dimension"], row["dimension"].replace("_", " ").title())
        value = "—" if row["value"] is None else f"{float(row['value']):.1f}"
        coverage = f"{float(row['coverage']) * 100:.0f}%"
        confidence = _STATUS_LABELS.get(row["confidence"], row["confidence"])
        consolidation = _STATUS_LABELS.get(row["consolidation_status"], row["consolidation_status"])
        return f"""
        <div class="score-row">
          <div><strong>{escape(_text(dimension))}</strong><small>{escape(_text(consolidation))}</small></div>
          <div class="score-value">{escape(value)}</div>
          <div><small>Cobertura</small><strong>{escape(coverage)}</strong></div>
          <div><small>Confiabilidade</small><strong>{escape(_text(confidence))}</strong></div>
        </div>
        """

    def _findings(self, *, findings: list[sqlite3.Row], evidence: dict[str, sqlite3.Row]) -> str:
        if not findings:
            return "<section><h2>Problemas Identificados e evidências</h2><p class='muted'>Nenhum finding persistido foi fornecido para o relatório.</p></section>"
        cards = []
        for finding in findings:
            evidence_ids = tuple(str(value) for value in _json_list(finding["evidence_ids"]))
            ev_html = "".join(self._evidence_item(evidence_id, evidence.get(evidence_id)) for evidence_id in evidence_ids)
            observed = _pretty_json(finding["observed_value"])
            cards.append(
                f"""
                <article class="finding">
                  <div class="finding-head"><span class="badge severity-{escape(finding['severity'].lower())}">{escape(finding['severity'])}</span><span class="rule">{escape(finding['rule_id'])}</span></div>
                  <h3>{escape(_text(finding['title']))}</h3>
                  <p><strong>Dispositivo:</strong> {escape(_text(finding['device']))} · <strong>Categoria:</strong> {escape(_text(finding['category']))}</p>
                  <p><strong>Condição esperada:</strong> {escape(_text(finding['expected_condition'] or 'Não informada'))}</p>
                  <details><summary>Valor observado</summary><pre>{escape(observed)}</pre></details>
                  <details><summary>Evidências rastreáveis ({len(evidence_ids)})</summary>{ev_html}</details>
                </article>
                """
            )
        return f"<section><h2>Problemas Identificados e evidências</h2>{''.join(cards)}</section>"

    @staticmethod
    def _evidence_item(evidence_id: str, row: sqlite3.Row | None) -> str:
        if row is None:
            return f"<div class='evidence'><strong>{escape(evidence_id)}</strong><p class='muted'>Referência não reaberta no momento da geração.</p></div>"
        observed = _pretty_json(row["observed_value"])
        return f"""
        <div class="evidence">
          <strong>{escape(evidence_id)}</strong>
          <span>{escape(_text(row['evidence_type']))} · {escape(_text(row['source']))}</span>
          <pre>{escape(observed)}</pre>
        </div>
        """

    def _recommendations(self, *, recommendations: list[sqlite3.Row], groups: dict[str, sqlite3.Row]) -> str:
        if not recommendations:
            return "<section><h2>Prioridades e recomendações</h2><p class='muted'>Nenhuma recomendação persistida disponível.</p></section>"
        cards = []
        for recommendation in recommendations:
            group = groups.get(recommendation["remediation_group_id"])
            affected = ""
            if group is not None:
                affected_findings = _json_list(group["affected_findings"])
                affected_pages = _json_list(group["affected_pages"])
                affected = f"<p><strong>Escopo:</strong> {len(affected_findings)} finding(s), {len(affected_pages)} página(s). <strong>Causa:</strong> {escape(_text(group['root_cause']))}</p>"
            cards.append(
                f"""
                <article class="recommendation">
                  <div class="finding-head"><span class="badge priority">{escape(_PRIORITY_LABELS.get(recommendation['priority_class'], recommendation['priority_class']))}</span><span class="rule">{float(recommendation['priority_score']):.2f}</span></div>
                  <h3>{escape(_text(recommendation['title']))}</h3>
                  <p>{escape(_text(recommendation['description']))}</p>
                  {affected}
                  <p><strong>Impacto:</strong> {escape(_text(recommendation['impact']))} · <strong>Esforço:</strong> {escape(_text(recommendation['effort']))} · <strong>Confiabilidade:</strong> {escape(_text(recommendation['confidence']))}</p>
                </article>
                """
            )
        return f"<section><h2>Prioridades e recomendações</h2>{''.join(cards)}</section>"

    def _limitations(self, *, audit_mode: AuditMode | None, limitations: tuple[str, ...]) -> str:
        items = [
            "Notas representam somente regras efetivamente avaliadas; cobertura e confiabilidade devem ser lidas em conjunto.",
            "Desktop e Mobile são independentes e não são combinados em uma única nota.",
            "Findings e recomendações são limitados ao universo efetivamente auditado e às evidências persistidas.",
        ]
        items.extend(_text(item) for item in limitations)
        if audit_mode is AuditMode.NO_AI:
            items.append("Avaliações semânticas dependentes de IA podem estar Não Determinadas, reduzindo cobertura sem penalizar o website.")
        html = "".join(f"<li>{escape(item)}</li>" for item in dict.fromkeys(items))
        return f"<section><h2>Limitações</h2><ul>{html}</ul></section>"

    @staticmethod
    def _technical(*, audit: sqlite3.Row, pages: list[sqlite3.Row], executions: list[sqlite3.Row]) -> str:
        executions_html = "".join(
            f"<tr><td>{escape(_STATUS_LABELS.get(row['result'], row['result']))}</td><td>{int(row['n'])}</td></tr>"
            for row in executions
        ) or "<tr><td colspan='2'>Sem RuleExecutions</td></tr>"
        return f"""
        <section>
          <h2>Detalhes técnicos</h2>
          <div class="technical-grid">
            <div><strong>Auditor version</strong><span>{escape(_text(audit['auditor_version']))}</span></div>
            <div><strong>Ruleset version</strong><span>{escape(_text(audit['ruleset_version']))}</span></div>
            <div><strong>Template version</strong><span>{TEMPLATE_VERSION}</span></div>
            <div><strong>max_pages</strong><span>{int(audit['max_pages'])}</span></div>
            <div><strong>Páginas persistidas</strong><span>{len(pages)}</span></div>
          </div>
          <h3>Resultados de regras</h3>
          <table><thead><tr><th>Resultado</th><th>Quantidade</th></tr></thead><tbody>{executions_html}</tbody></table>
        </section>
        """

    @staticmethod
    def _glossary() -> str:
        terms = (
            ("Acessibilidade Técnica", "Condições técnicas para recuperação e acesso do conteúdo."),
            ("Capacidade de Indexação", "Sinais que permitem avaliar se uma URL pode participar do universo indexável."),
            ("Extração de Conteúdo", "Capacidade de identificar e recuperar conteúdo principal e contexto essencial."),
            ("Readiness", "Grau de preparação observado segundo as regras da auditoria; não equivale a garantia de desempenho externo."),
            ("Canonical (URL canônica)", "Sinal técnico de URL preferencial."),
            ("Soft 404", "Página com semântica de erro sem status HTTP apropriado."),
            ("Client-Side Rendering — CSR", "Renderização no navegador."),
            ("SPA", "Single-Page Application."),
            ("JSON-LD", "Formato comum de Dados Estruturados."),
        )
        rows = "".join(f"<dt>{escape(term)}</dt><dd>{escape(definition)}</dd>" for term, definition in terms)
        return f"<section><h2>Legenda e glossário</h2><dl>{rows}</dl></section>"

    @staticmethod
    def _document(*, title: str, body: str) -> str:
        css = """
        :root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#172033;background:#eef2f7;line-height:1.5}
        *{box-sizing:border-box}body{margin:0}.page{max-width:1180px;margin:0 auto;padding:32px 24px 72px}section,.hero{background:#fff;border:1px solid #dce3ec;border-radius:16px;padding:28px;margin:0 0 20px;box-shadow:0 8px 24px rgba(25,39,67,.05)}
        .hero{padding:38px}.eyebrow{font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#46566f}h1{font-size:2rem;line-height:1.15;margin:.5rem 0}.lead{max-width:860px;color:#536078}.meta-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-top:24px}.metric{background:#f6f8fb;border:1px solid #e5eaf1;border-radius:12px;padding:14px}.metric small,.score-row small{display:block;color:#657086}.metric strong{display:block;margin-top:4px;overflow-wrap:anywhere}.compact{margin-top:12px}
        h2{font-size:1.35rem;margin:0 0 18px}h3{font-size:1.02rem;margin:0 0 8px}.explain-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}.explain{border-left:3px solid #8794a8;padding:10px 14px;background:#fafbfd}.explain p{margin:0;color:#58657a}.notice{background:#f5f7fa;border:1px solid #dce3ec;border-radius:10px;padding:14px;margin:14px 0}.devices{display:grid;grid-template-columns:1fr 1fr;gap:16px}.device{border:1px solid #dce3ec;border-radius:12px;padding:16px}.score-row{display:grid;grid-template-columns:minmax(190px,2fr) 70px 90px 110px;gap:12px;align-items:center;border-top:1px solid #edf0f4;padding:12px 0}.score-row:first-child{border-top:0}.score-value{font-size:1.4rem;font-weight:800}.finding,.recommendation{border:1px solid #dce3ec;border-radius:12px;padding:18px;margin:12px 0}.finding-head{display:flex;align-items:center;justify-content:space-between;gap:12px}.badge{display:inline-block;border-radius:999px;padding:4px 9px;background:#eef2f7;font-size:.78rem;font-weight:800}.severity-critical{background:#f4dcdc}.severity-high{background:#f5e5dd}.severity-medium{background:#f3ecd8}.severity-low{background:#e9edf4}.priority{background:#e4e9f1}.rule{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#5b6679}.muted{color:#68758a}details{margin-top:10px}summary{cursor:pointer;font-weight:700}.evidence{border-top:1px solid #edf0f4;padding:10px 0}.evidence span{display:block;color:#637087;font-size:.85rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f6f8fb;border-radius:8px;padding:10px;font-size:.78rem}table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid #e8edf3;padding:9px}.technical-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}.technical-grid div{display:flex;flex-direction:column;background:#f8fafc;padding:10px;border-radius:8px}dl{display:grid;grid-template-columns:minmax(180px,280px) 1fr;gap:8px 18px}dt{font-weight:800}dd{margin:0;color:#59667a}
        footer{text-align:center;color:#6c778a;font-size:.82rem;padding:18px}@media(max-width:760px){.devices{grid-template-columns:1fr}.score-row{grid-template-columns:1fr 60px}.score-row>div:nth-child(3),.score-row>div:nth-child(4){padding-left:0}dl{grid-template-columns:1fr}section,.hero{padding:20px}.page{padding:16px}}
        @media print{body{background:#fff}.page{max-width:none;padding:0}section,.hero{box-shadow:none;break-inside:avoid}.finding,.recommendation{break-inside:avoid}}
        """
        return f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>{css}</style></head>
<body><main class="page">{body}<footer>Relatório estático · {TEMPLATE_VERSION} · gerado a partir de dados persistidos da auditoria.</footer></main></body>
</html>"""


def write_report(*, workspace: AuditWorkspace, html: str, filename: str = "report.html") -> Path:
    path = workspace.root / filename
    temporary = workspace.root / f".{filename}.tmp"
    temporary.write_text(html, encoding="utf-8", newline="\n")
    temporary.replace(path)
    return path


def new_report_record(*, audit_id: str, auditor_version: str, file_path: str) -> ReportRecord:
    return ReportRecord(
        report_id=new_id("RPT"),
        audit_id=audit_id,
        format="HTML",
        status="GENERATED",
        generated_at=utc_now(),
        template_version=TEMPLATE_VERSION,
        auditor_version=auditor_version,
        file_path=file_path,
    )


def _metric(label: str, value: Any) -> str:
    return f"<div class='metric'><small>{escape(_text(label))}</small><strong>{escape(_text(value))}</strong></div>"


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


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


def _pretty_json(value: Any) -> str:
    parsed: Any = value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = value
    sanitized = _redact(parsed)
    if isinstance(sanitized, (dict, list, tuple)):
        return json.dumps(sanitized, ensure_ascii=False, indent=2, sort_keys=True)
    return _text(sanitized)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]" if _SENSITIVE_KEY.search(str(key)) else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact(item) for item in value)
    return value
