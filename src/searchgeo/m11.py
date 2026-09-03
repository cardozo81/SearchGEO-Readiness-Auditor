"""M11/M14/M15/M16/M17 — Static HTML Report orchestration."""

from __future__ import annotations

from dataclasses import dataclass
import re
import sqlite3

from searchgeo.m14_persistence import M14Persistence
from searchgeo.m14_reporting import TEMPLATE_VERSION, _metric, new_m14_report_record
from searchgeo.m15_reporting import write_remediation_report
from searchgeo.m15_style_overrides import SCORE_LAYOUT_CSS
from searchgeo.m16_root_cause import materialize_root_causes
from searchgeo.m17_precision import materialize_m17_precision
from searchgeo.m17_reporting import M17RemediationReportBuilder, M17ReportBuilder
from searchgeo.persistence import AuditPersistence, AuditWorkspace
from searchgeo import reporting as reporting_module
from searchgeo.reporting import ReportPersistence, write_report

# REPORT-GEO-003 remains the page-oriented report contract. M17 tightens the
# remediation projection without changing SCORE-GEO-001 or RuleResult semantics.
reporting_module.TEMPLATE_VERSION = TEMPLATE_VERSION


def _ai_usage_status(semantic: list[sqlite3.Row]) -> str:
    """Return the human state of external semantic AI for this audit report."""

    providers = {str(row["provider"]).upper() for row in semantic if row["provider"]}
    if "OPENAI" in providers:
        return "SIM"
    if "UNAVAILABLE" in providers:
        return "TENTATIVA SEM SUCESSO"
    return "NÃO"


class _PersistedInputAwareReportBuilder(M17ReportBuilder):
    """Use raw operator input counts while rendering the deduplicated URL set."""

    def __init__(self, workspace: AuditWorkspace) -> None:
        super().__init__()
        self._workspace = workspace
        self._input_summary = None

    def build(self, *, audit_id: str, workspace: AuditWorkspace) -> str:
        with M14Persistence(workspace) as m14:
            self._input_summary = m14.get_input_summary(audit_id)
        html = super().build(audit_id=audit_id, workspace=workspace)
        html = html.replace("</style>", f"{SCORE_LAYOUT_CSS}</style>", 1)

        # An empty audit has no page context to which external best-practice
        # references can be applied. Keep labels but remove external hrefs in
        # that degenerate report, preserving the long-standing self-contained
        # empty-report invariant. Real audited page universes keep the links.
        with sqlite3.connect(workspace.database) as connection:
            page_count = connection.execute(
                "SELECT COUNT(*) FROM pages WHERE audit_id = ?", (audit_id,)
            ).fetchone()[0]
        if page_count == 0:
            html = re.sub(
                r"<a href='https?://[^']+' target='_blank' rel='noopener'>(.*?)</a>",
                r"\1",
                html,
                flags=re.DOTALL,
            )
        return html

    def _executive(
        self,
        *,
        audit: sqlite3.Row,
        domain: str,
        target_type: str,
        supplied_count: int,
        audited_count: int,
        semantic: list[sqlite3.Row],
    ) -> str:
        summary = self._input_summary
        if summary is not None:
            supplied_count = summary.supplied_count
            target_type = summary.input_mode

        html = super()._executive(
            audit=audit,
            domain=domain,
            target_type=target_type,
            supplied_count=supplied_count,
            audited_count=audited_count,
            semantic=semantic,
        )

        providers = sorted({str(row["provider"]) for row in semantic if row["provider"]})
        legacy_ai_used = any(provider.casefold() not in {"none", "fallback", ""} for provider in providers)
        return html.replace(
            _metric("Uso de IA", "SIM" if legacy_ai_used else "NÃO"),
            _metric("Uso de IA", _ai_usage_status(semantic)),
            1,
        )


@dataclass(frozen=True, slots=True)
class M11ExecutionResult:
    report_id: str
    file_path: str
    template_version: str
    remediation_file_path: str = "remediation.html"


def execute_m11(
    *,
    audit_id: str,
    persistence: AuditPersistence,
    workspace: AuditWorkspace,
) -> M11ExecutionResult:
    audit = persistence.audits.get(audit_id)
    if audit is None:
        raise ValueError(f"audit not found: {audit_id}")

    # M16 materializes the evidence-backed root cause. M17 then adds a separate
    # precision projection (reason code, observed element state and target
    # selector) so old audit databases remain compatible and no M16 record is
    # destructively rewritten.
    materialize_root_causes(audit_id=audit_id, workspace=workspace)
    materialize_m17_precision(audit_id=audit_id, workspace=workspace)

    html = _PersistedInputAwareReportBuilder(workspace).build(
        audit_id=audit_id,
        workspace=workspace,
    )
    path = write_report(workspace=workspace, html=html)

    remediation_html = M17RemediationReportBuilder().build(
        audit_id=audit_id,
        workspace=workspace,
    )
    remediation_path = write_remediation_report(workspace=workspace, html=remediation_html)

    record = new_m14_report_record(
        audit_id=audit_id,
        auditor_version=audit.auditor_version,
        file_path=path.name,
    )
    with ReportPersistence(workspace) as reports:
        reports.add(record)
        reopened = reports.get(record.report_id)
        if reopened != record:
            raise RuntimeError("report metadata is not reproducible after persistence")

    return M11ExecutionResult(
        report_id=record.report_id,
        file_path=record.file_path,
        template_version=record.template_version,
        remediation_file_path=remediation_path.name,
    )
