"""M12 end-to-end audit orchestration for the stable local baseline."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from searchgeo import __version__
from searchgeo.content_extractability import execute_content_extractability
from searchgeo.domain import (
    Audit,
    AuditStatus,
    AuditTarget,
    CompletionStatus,
    TargetType,
    new_id,
    utc_now,
)
from searchgeo.m2 import execute_m2
from searchgeo.m3 import execute_m3
from searchgeo.m4 import execute_m4
from searchgeo.m5 import execute_m5
from searchgeo.m6 import execute_m6
from searchgeo.m7 import execute_m7
from searchgeo.m8 import execute_m8
from searchgeo.m9 import execute_m9
from searchgeo.m10 import execute_m10
from searchgeo.m11 import execute_m11
from searchgeo.persistence import AuditPersistence, AuditWorkspace
from searchgeo.pre_scoring_rules import execute_pre_scoring_rules
from searchgeo.semantic import NoneProvider, SemanticAnalysisProvider
from searchgeo.url_utils import normalize_url, normalized_origin


@dataclass(frozen=True, slots=True)
class AuditRunResult:
    audit_id: str
    audit_root: Path
    report_path: Path
    completion_status: CompletionStatus
    audited_pages: int
    finding_count: int
    recommendation_count: int


def run_audit(
    target: str,
    *,
    audits_root: str | Path = "audits",
    project_name: str | None = None,
    language: str = "pt-BR",
    market: str = "BR",
    max_pages: int = 100,
    semantic_provider: SemanticAnalysisProvider | None = None,
    discovery_engine: Any | None = None,
    renderer: Any | None = None,
    lazy_probe: Any | None = None,
) -> AuditRunResult:
    """Execute the approved M1–M11 pipeline and leave a reopenable local audit workspace.

    Optional engine/renderer/probe/provider injection exists for deterministic critical
    tests. Production callers omit them and use the real local adapters.
    """

    normalized_target = normalize_url(target)
    if max_pages <= 0:
        raise ValueError("max_pages must be greater than zero")
    project = (project_name or urlsplit(normalized_target).hostname or normalized_target).strip()
    if not project:
        raise ValueError("project_name must not be empty")

    audit_id = new_id("AUD")
    workspace = AuditWorkspace.create(Path(audits_root), audit_id)
    target_type = _target_type(normalized_target)
    audit = Audit(
        audit_id=audit_id,
        project_name=project,
        status=AuditStatus.INITIALIZING,
        primary_language=language,
        market=market,
        max_pages=max_pages,
        capabilities=("filesystem", "sqlite", "desktop_mobile"),
        created_at=utc_now(),
        started_at=utc_now(),
        auditor_version=__version__,
        ruleset_version="1",
    )
    audit_target = AuditTarget(
        target_id=new_id("TGT"),
        audit_id=audit_id,
        input_url=normalized_target,
        normalized_origin=normalized_origin(normalized_target),
        target_type=target_type,
    )

    with AuditPersistence(workspace) as persistence:
        persistence.audits.add(audit)
        persistence.targets.add(audit_target)
        try:
            m2 = execute_m2(
                audit,
                audit_target,
                persistence,
                workspace,
                engine=discovery_engine,
            )
            m3 = execute_m3(m2, persistence, workspace, renderer=renderer)
            m4 = execute_m4(m3, persistence, workspace)
            m5 = execute_m5(audit, audit_target, m2, m3, m4, persistence, workspace)
            m6 = execute_m6(
                audit_id=audit_id,
                m2_result=m2,
                m3_result=m3,
                m4_result=m4,
                m5_result=m5,
                persistence=persistence,
                workspace=workspace,
                lazy_probe=lazy_probe,
            )
            content = execute_content_extractability(
                audit_id=audit_id,
                m3_result=m3,
                persistence=persistence,
                workspace=workspace,
            )
            m7 = execute_m7(
                audit_id=audit_id,
                m3_result=m3,
                m4_result=m4,
                m5_result=m5,
                m6_result=m6,
                persistence=persistence,
                workspace=workspace,
                provider=semantic_provider or NoneProvider(),
            )

            _set_status(persistence, audit_id, AuditStatus.COMPARING)
            m8 = execute_m8(
                audit_id=audit_id,
                m3_result=m3,
                persistence=persistence,
                workspace=workspace,
            )

            findings_before_integrity = _unique(
                m5.finding_ids,
                m6.finding_ids,
                content.finding_ids,
                m7.finding_ids,
                m8.finding_ids,
            )
            pre_scoring = execute_pre_scoring_rules(
                audit_id=audit_id,
                m2_result=m2,
                m3_result=m3,
                persistence=persistence,
                workspace=workspace,
                finding_ids_to_validate=findings_before_integrity,
            )

            _set_status(persistence, audit_id, AuditStatus.SCORING)
            scoring_execution_ids = _unique(
                m5.rule_execution_ids,
                m6.rule_execution_ids,
                content.rule_execution_ids,
                m7.rule_execution_ids,
                m8.rule_execution_ids,
                pre_scoring.rule_execution_ids,
            )
            execute_m9(
                audit_id=audit_id,
                rule_execution_ids=scoring_execution_ids,
                persistence=persistence,
                workspace=workspace,
            )

            _set_status(persistence, audit_id, AuditStatus.RECOMMENDING)
            all_finding_ids = _unique(
                findings_before_integrity,
                pre_scoring.finding_ids,
            )
            m10 = execute_m10(
                audit_id=audit_id,
                finding_ids=all_finding_ids,
                persistence=persistence,
                workspace=workspace,
            )

            _set_status(persistence, audit_id, AuditStatus.REPORTING)
            m11 = execute_m11(
                audit_id=audit_id,
                persistence=persistence,
                workspace=workspace,
            )

            current = persistence.audits.get(audit_id)
            if current is None:
                raise RuntimeError(f"audit disappeared before completion: {audit_id}")
            completion = (
                CompletionStatus.COMPLETE_WITH_LIMITATIONS
                if current.limitations or current.audit_mode is None or current.audit_mode.value != "FULL"
                else CompletionStatus.COMPLETE
            )
            persistence.audits.complete(audit_id, completion)

            return AuditRunResult(
                audit_id=audit_id,
                audit_root=workspace.root,
                report_path=workspace.root / m11.file_path,
                completion_status=completion,
                audited_pages=len(m2.page_ids),
                finding_count=len(all_finding_ids),
                recommendation_count=len(m10.recommendation_ids),
            )
        except Exception:
            current = persistence.audits.get(audit_id)
            if current is not None and current.status not in {AuditStatus.COMPLETED, AuditStatus.CANCELLED}:
                persistence.audits.update(replace(current, status=AuditStatus.FAILED))
            raise


def _set_status(persistence: AuditPersistence, audit_id: str, status: AuditStatus) -> None:
    audit = persistence.audits.get(audit_id)
    if audit is None:
        raise RuntimeError(f"audit not found while setting status: {audit_id}")
    persistence.audits.update(replace(audit, status=status))


def _target_type(normalized_target: str) -> TargetType:
    parsed = urlsplit(normalized_target)
    return TargetType.DOMAIN if parsed.path in {"", "/"} and not parsed.query else TargetType.URL


def _unique(*groups: tuple[str, ...]) -> tuple[str, ...]:
    values: list[str] = []
    for group in groups:
        values.extend(group)
    return tuple(dict.fromkeys(values))
