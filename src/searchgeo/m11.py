"""M11/M14/M15 — Static HTML Report orchestration."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from searchgeo.m14_persistence import M14Persistence
from searchgeo.m14_reporting import TEMPLATE_VERSION, new_m14_report_record
from searchgeo.m15_reporting import M15ReportBuilder, M15RemediationReportBuilder, write_remediation_report
from searchgeo.persistence import AuditPersistence, AuditWorkspace
from searchgeo import reporting as reporting_module
from searchgeo.reporting import ReportPersistence, write_report

# REPORT-GEO-003 remains the page-oriented report contract. M15 changes its UX
# and adds REMEDIATION-GEO-001 as a second derived projection without changing
# SCORE-GEO-001 or persisted finding semantics.
reporting_module.TEMPLATE_VERSION = TEMPLATE_VERSION


class _PersistedInputAwareReportBuilder(M15ReportBuilder):
    """Use raw operator input counts while rendering the deduplicated URL set."""

    def __init__(self, workspace: AuditWorkspace) -> None:
        self._workspace = workspace
        self._input_summary = None

    def build(self, *, audit_id: str, workspace: AuditWorkspace) -> str:
        with M14Persistence(workspace) as m14:
            self._input_summary = m14.get_input_summary(audit_id)
        return super().build(audit_id=audit_id, workspace=workspace)

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
        return super()._executive(
            audit=audit,
            domain=domain,
            target_type=target_type,
            supplied_count=supplied_count,
            audited_count=audited_count,
            semantic=semantic,
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

    html = _PersistedInputAwareReportBuilder(workspace).build(
        audit_id=audit_id,
        workspace=workspace,
    )
    path = write_report(workspace=workspace, html=html)

    remediation_html = M15RemediationReportBuilder().build(
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
