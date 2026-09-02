"""M11/M14 — Static HTML Report orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from searchgeo.m14_reporting import M14ReportBuilder, TEMPLATE_VERSION, new_m14_report_record
from searchgeo.persistence import AuditPersistence, AuditWorkspace
from searchgeo import reporting as reporting_module
from searchgeo.reporting import ReportPersistence, write_report

# REPORT-GEO-003 is the active report contract once M11 is orchestrated through
# M14.  Keep the legacy reporting module's exported constant aligned so callers
# that import TEMPLATE_VERSION from searchgeo.reporting observe the active
# contract without duplicating the large stable M13 renderer.
reporting_module.TEMPLATE_VERSION = TEMPLATE_VERSION


@dataclass(frozen=True, slots=True)
class M11ExecutionResult:
    report_id: str
    file_path: str
    template_version: str


def execute_m11(
    *,
    audit_id: str,
    persistence: AuditPersistence,
    workspace: AuditWorkspace,
) -> M11ExecutionResult:
    audit = persistence.audits.get(audit_id)
    if audit is None:
        raise ValueError(f"audit not found: {audit_id}")

    html = M14ReportBuilder().build(audit_id=audit_id, workspace=workspace)
    path = write_report(workspace=workspace, html=html)
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
    )
