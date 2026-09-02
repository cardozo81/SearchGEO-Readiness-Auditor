"""Critical M9 scoring tests."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from searchgeo.domain import DeviceContext, RuleExecution, RuleResult
from searchgeo.scoring import ConsolidationStatus, ScoringEngine


_NOW = datetime(2026, 9, 2, 17, 0, tzinfo=timezone.utc)


def _execution(rule_id: str, result: RuleResult, *, page: str = "P1", device: DeviceContext | None = DeviceContext.DESKTOP) -> RuleExecution:
    return RuleExecution(
        rule_execution_id=f"REX-{rule_id}-{result.value}-{page}-{device.value if device else 'GLOBAL'}",
        audit_id="AUD-1", rule_id=rule_id, rule_version="1", page_id=page,
        snapshot_id=None, device=device, result=result, observed_value={}, expected_condition="fixture",
        evidence_ids=("EVD-1",), executed_at=_NOW,
    )


class M9ScoringTests(unittest.TestCase):
    def test_unknown_reduces_coverage_without_reducing_quality_factor(self) -> None:
        result = ScoringEngine().score(
            audit_id="AUD-1",
            executions=(
                _execution("BR-GEO-028", RuleResult.PASS),
                _execution("BR-GEO-029", RuleResult.UNKNOWN),
                _execution("BR-GEO-030", RuleResult.PASS),
            ),
        )
        score = next(item for item in result.scores if item.device is DeviceContext.DESKTOP and item.dimension == "SEMANTIC_STRUCTURE")
        self.assertEqual(score.value, 100.0)
        self.assertAlmostEqual(score.coverage, 2 / 3, places=6)
        self.assertEqual(score.consolidation_status, ConsolidationStatus.PARTIAL)

    def test_max_impact_collapses_correlated_fail_and_pass_once(self) -> None:
        result = ScoringEngine().score(
            audit_id="AUD-1",
            executions=(
                _execution("BR-GEO-011", RuleResult.PASS),
                _execution("BR-GEO-012", RuleResult.FAIL),
                _execution("BR-GEO-015", RuleResult.PASS),
            ),
        )
        score = next(item for item in result.scores if item.device is DeviceContext.DESKTOP and item.dimension == "INDEXABILITY")
        contributions = [item for item in result.contributions if item.score_id == score.score_id]
        self.assertEqual(len(contributions), 1)
        self.assertEqual(contributions[0].result, RuleResult.FAIL)
        self.assertEqual(score.value, 0.0)

    def test_overall_remains_not_consolidated_when_required_dimensions_missing(self) -> None:
        result = ScoringEngine().score(
            audit_id="AUD-1",
            executions=(_execution("BR-GEO-005", RuleResult.PASS),),
        )
        overall = result.overall_by_device[DeviceContext.DESKTOP]
        self.assertIsNone(overall.value)
        self.assertEqual(overall.consolidation_status, ConsolidationStatus.NOT_CONSOLIDATED)

    def test_device_independent_execution_contributes_once_to_each_device(self) -> None:
        result = ScoringEngine().score(
            audit_id="AUD-1",
            executions=(_execution("BR-GEO-005", RuleResult.PASS, device=None),),
        )
        desktop = next(item for item in result.scores if item.device is DeviceContext.DESKTOP and item.dimension == "TECHNICAL_ACCESSIBILITY")
        mobile = next(item for item in result.scores if item.device is DeviceContext.MOBILE and item.dimension == "TECHNICAL_ACCESSIBILITY")
        self.assertEqual(desktop.value, 100.0)
        self.assertEqual(mobile.value, 100.0)


if __name__ == "__main__":
    unittest.main()
