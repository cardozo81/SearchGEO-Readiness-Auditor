"""M8 — Desktop × Mobile comparison and BR-GEO-052."""

from __future__ import annotations

from dataclasses import dataclass

from searchgeo.comparison import DeviceComparator, DeviceComparisonOutcome
from searchgeo.domain import (
    DeviceContext,
    EvidenceType,
    Finding,
    FindingDevice,
    RuleExecution,
    RuleResult,
    Severity,
    new_id,
    utc_now,
)
from searchgeo.evidence import EvidenceManager
from searchgeo.m3 import M3ExecutionResult
from searchgeo.persistence import AuditPersistence, AuditWorkspace
from searchgeo.semantic_persistence import SemanticPersistence


_RULE_ID = "BR-GEO-052"
_RULE_VERSION = "1"


@dataclass(frozen=True, slots=True)
class M8ExecutionResult:
    rule_execution_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    outcomes_by_page: dict[str, DeviceComparisonOutcome]


def execute_m8(
    *,
    audit_id: str,
    m3_result: M3ExecutionResult,
    persistence: AuditPersistence,
    workspace: AuditWorkspace,
) -> M8ExecutionResult:
    comparator = DeviceComparator()
    manager = EvidenceManager(persistence)
    execution_ids: list[str] = []
    finding_ids: list[str] = []
    outcomes: dict[str, DeviceComparisonOutcome] = {}

    with SemanticPersistence(workspace) as semantic:
        for page_id, per_device in m3_result.snapshot_ids.items():
            desktop_id = per_device.get(DeviceContext.DESKTOP)
            mobile_id = per_device.get(DeviceContext.MOBILE)
            desktop = persistence.snapshots.get(desktop_id) if desktop_id else None
            mobile = persistence.snapshots.get(mobile_id) if mobile_id else None

            comparison = comparator.compare(
                desktop=desktop,
                mobile=mobile,
                workspace_root=workspace.root,
                desktop_entities=semantic.list_entities(desktop_id) if desktop_id else (),
                mobile_entities=semantic.list_entities(mobile_id) if mobile_id else (),
                desktop_assessments=semantic.list_assessments(desktop_id) if desktop_id else (),
                mobile_assessments=semantic.list_assessments(mobile_id) if mobile_id else (),
            )
            outcomes[page_id] = comparison.outcome

            if comparison.outcome is DeviceComparisonOutcome.NOT_APPLICABLE:
                result = RuleResult.NOT_APPLICABLE
                reason = "NO_DEVICE_SNAPSHOTS"
            elif comparison.outcome is DeviceComparisonOutcome.UNKNOWN:
                result = RuleResult.UNKNOWN
                reason = "ONE_DEVICE_SNAPSHOT_MISSING"
            elif comparison.materially_problematic:
                result = RuleResult.WARNING
                reason = "MATERIAL_DEVICE_DIFFERENCE"
            else:
                result = RuleResult.PASS
                reason = None

            observed = {
                "classification": comparison.outcome.value,
                "changed_fields": list(comparison.changed_fields),
                "material_fields": list(comparison.material_fields),
                "desktop": comparison.desktop,
                "mobile": comparison.mobile,
                "limitations": list(comparison.limitations),
            }
            evidence = manager.record(
                audit_id=audit_id,
                page_id=page_id,
                snapshot_id=None,
                device=None,
                evidence_type=EvidenceType.COMPARISON,
                source="device-comparator:BR-GEO-052",
                observed_value=observed,
            )
            execution = RuleExecution(
                rule_execution_id=new_id("REX"),
                audit_id=audit_id,
                rule_id=_RULE_ID,
                rule_version=_RULE_VERSION,
                page_id=page_id,
                snapshot_id=None,
                device=None,
                result=result,
                observed_value=observed,
                expected_condition=(
                    "material Desktop/Mobile differences are explicitly classified; "
                    "difference alone is not treated as a defect"
                ),
                evidence_ids=(evidence.evidence_id,),
                executed_at=utc_now(),
                error=None,
            )
            persistence.rule_executions.add(execution)
            execution_ids.append(execution.rule_execution_id)

            if result is RuleResult.WARNING:
                finding = Finding(
                    finding_id=new_id("FND"),
                    audit_id=audit_id,
                    rule_id=_RULE_ID,
                    rule_execution_id=execution.rule_execution_id,
                    page_id=page_id,
                    device=FindingDevice.BOTH,
                    category="DESKTOP_MOBILE",
                    severity=Severity.MEDIUM,
                    source="deterministic-device-comparison",
                    title="Material Desktop/Mobile difference detected",
                    observed_value=observed,
                    expected_condition=execution.expected_condition,
                    evidence_ids=execution.evidence_ids,
                    status="OPEN",
                )
                persistence.findings.add(finding)
                finding_ids.append(finding.finding_id)

    return M8ExecutionResult(tuple(execution_ids), tuple(finding_ids), outcomes)
