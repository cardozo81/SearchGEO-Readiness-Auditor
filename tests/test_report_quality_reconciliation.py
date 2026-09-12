from __future__ import annotations

import json
import sqlite3

from rasai import report_quality_reconciliation as reconciliation


def test_lighthouse_timeout_reason_accepts_pagespeed_insights_service() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        """CREATE TABLE web_performance_attempts (
            audit_id TEXT, service TEXT, status TEXT, http_status INTEGER,
            duration_ms INTEGER, error_code TEXT, error_message TEXT, created_at TEXT
        )"""
    )
    connection.execute(
        "INSERT INTO web_performance_attempts VALUES (?,?,?,?,?,?,?,?)",
        (
            "AUD-1",
            "PAGESPEED_INSIGHTS",
            "ERROR",
            None,
            120006,
            "WALL_CLOCK_TIMEOUT",
            "wall-clock deadline exceeded after 120s",
            "2026-09-12T20:00:00Z",
        ),
    )

    detail = reconciliation._lighthouse_unavailable_detail(connection, "AUD-1")

    assert detail is not None
    assert "WALL_CLOCK_TIMEOUT" in detail
    assert "120s" in detail
    assert "Nenhuma categoria Lighthouse válida foi persistida" in detail


def test_scoring_overall_uses_readiness_state_not_numeric_score_alone() -> None:
    row = {
        "device": "MOBILE",
        "value": 91.0,
        "coverage": 0.95,
        "confidence": "MEDIUM",
        "consolidation_status": "CONSOLIDATED",
        "limitations": json.dumps(
            [
                "CRITICAL_GATE:DISCOVERY:WARNING",
                "CRITICAL_GATE:INDEXABILITY:WARNING",
                "CRITICAL_GATE:EXTRACTION:PASS",
                "READINESS_STATUS:ATTENTION",
            ]
        ),
    }
    html = (
        "<table><tr class='result-state-good'><td>MOBILE</td><td>91.0/100</td>"
        "<td>95%</td><td>Média</td><td>Consolidado</td></tr></table>"
    )

    updated = reconciliation._reconcile_sari_scoring_html(html, [row])

    assert "score-condition-near" in updated
    assert "result-state-warn" in updated
    assert "Readiness requer atenção" in updated
    assert "Qualidade medida: Excelente (90-100)" in updated


def test_owned_identifier_sanitizer_preserves_arbitrary_audited_model_names() -> None:
    html = (
        "Produto M25 industrial; opaque=T-M2Woib; "
        "M18-SEMANTIC-22-v1 M20-CONTENT-REMEDIATION-v3 "
        "M24-ROBOTS-ABSENT rasai_m24_technical_remediation M20_INVALID_ROOT_SCHEMA"
    )

    updated = reconciliation._sanitize_owned_internal_tokens(html)

    assert "Produto M25 industrial" in updated
    assert "T-M2Woib" in updated
    assert "M18-SEMANTIC-22-v1" not in updated
    assert "M20-CONTENT-REMEDIATION-v3" not in updated
    assert "M24-ROBOTS-ABSENT" not in updated
    assert "rasai_m24_technical_remediation" not in updated
    assert "M20_INVALID_ROOT_SCHEMA" not in updated
    assert "CONTENT_REMEDIATION_INVALID_ROOT_SCHEMA" in updated


def test_ai_schemas_require_current_degradation_and_expected_benefit() -> None:
    from rasai import improvement_intelligence, m20_ai, provider_extensions_m20

    ii_originals = (
        improvement_intelligence._schema,
        improvement_intelligence._validate_ai_payload,
        improvement_intelligence._instructions,
        improvement_intelligence.ImprovementConfig.fingerprint,
        getattr(improvement_intelligence, "_rasai_benefit_degradation_contract", None),
    )
    m20_originals = (
        m20_ai.content_remediation_schema,
        m20_ai._validate_response,
        getattr(m20_ai, "_rasai_benefit_degradation_contract", None),
        provider_extensions_m20.content_remediation_schema,
        provider_extensions_m20._validate_response,
        provider_extensions_m20._instructions,
    )
    try:
        if hasattr(improvement_intelligence, "_rasai_benefit_degradation_contract"):
            delattr(improvement_intelligence, "_rasai_benefit_degradation_contract")
        if hasattr(m20_ai, "_rasai_benefit_degradation_contract"):
            delattr(m20_ai, "_rasai_benefit_degradation_contract")

        reconciliation.install()

        improvement_schema = improvement_intelligence._schema(
            [{"finding_id": "F1", "evidence_ids": ["E1"]}], 5
        )
        improvement_item = improvement_schema["properties"]["recommendations"]["items"]
        assert "current_degradation" in improvement_item["required"]
        assert "expected_benefit" in improvement_item["required"]
        assert improvement_item["properties"]["current_degradation"]["minLength"] == 1
        assert improvement_item["properties"]["expected_benefit"]["minLength"] == 1

        content_schema = m20_ai.content_remediation_schema()
        content_item = content_schema["properties"]["suggestions"]["items"]
        assert "current_degradation" in content_item["required"]
        assert "expected_benefit" in content_item["required"]

        baseline = ii_originals[3](improvement_intelligence.ImprovementConfig())
        effective = improvement_intelligence.ImprovementConfig().fingerprint()
        assert baseline != effective
    finally:
        improvement_intelligence._schema = ii_originals[0]
        improvement_intelligence._validate_ai_payload = ii_originals[1]
        improvement_intelligence._instructions = ii_originals[2]
        improvement_intelligence.ImprovementConfig.fingerprint = ii_originals[3]
        if ii_originals[4] is None:
            if hasattr(improvement_intelligence, "_rasai_benefit_degradation_contract"):
                delattr(improvement_intelligence, "_rasai_benefit_degradation_contract")
        else:
            improvement_intelligence._rasai_benefit_degradation_contract = ii_originals[4]

        m20_ai.content_remediation_schema = m20_originals[0]
        m20_ai._validate_response = m20_originals[1]
        if m20_originals[2] is None:
            if hasattr(m20_ai, "_rasai_benefit_degradation_contract"):
                delattr(m20_ai, "_rasai_benefit_degradation_contract")
        else:
            m20_ai._rasai_benefit_degradation_contract = m20_originals[2]
        provider_extensions_m20.content_remediation_schema = m20_originals[3]
        provider_extensions_m20._validate_response = m20_originals[4]
        provider_extensions_m20._instructions = m20_originals[5]
