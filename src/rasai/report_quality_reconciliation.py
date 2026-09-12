"""Final public-report quality and AI recommendation contract reconciliation.

This layer is projection/runtime-only. It does not change audited website facts,
SARI arithmetic, Lighthouse/CrUX measurements, or raw AI exchange evidence.
"""
from __future__ import annotations

from copy import deepcopy
from html import escape
from hashlib import sha256
import re
import sqlite3
from typing import Any, Mapping, Sequence

from rasai.persistence import AuditWorkspace
from rasai.public_report_safety import normalize_owned_public_report_text
from rasai.sari_readiness_presentation import public_readiness_condition

IMPROVEMENT_CONTRACT_VERSION = "IMPROVEMENT-INTELLIGENCE-001"

_GENERIC_NO_DATA = (
    "Esta capacidade é opcional. Ela pode não ter sido solicitada, configurada, "
    "aplicável ou pode não ter retornado dados nesta auditoria."
)

_OWNED_TOKEN_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("M18-SEMANTIC-22-v1", "SEMANTIC-ANALYSIS-22-v1"),
    ("M20-CONTENT-REMEDIATION-v3", "CONTENT-REMEDIATION-v3"),
    ("M24-TECHNICAL-REMEDIATION-v2", "TECHNICAL-REMEDIATION-v2"),
    ("rasai_m24_technical_remediation", "rasai_technical_remediation"),
    ("M24-ROBOTS-ABSENT", "CRAWLING-ROBOTS-ABSENT"),
    ("M24-SITEMAP-ABSENT", "CRAWLING-SITEMAP-ABSENT"),
    ("M24-DISCOVERY-INDEXNOW", "CRAWLING-DISCOVERY-INDEXNOW"),
    ("M24-LLMS-ABSENT", "CRAWLING-LLMS-ABSENT"),
    ("M24-LLMS-DISCOVERY-SUMMARY", "CRAWLING-LLMS-DISCOVERY-SUMMARY"),
    ("M24-RESOURCE-SITEMAP-BASELINE", "CRAWLING-RESOURCE-SITEMAP-BASELINE"),
    ("M24-RESOURCE-ROBOTS-BASELINE", "CRAWLING-RESOURCE-ROBOTS-BASELINE"),
    ("M2 physical HTTP acquisition", "aquisição HTTP física"),
    ("aquisição física M2 por URL", "aquisição HTTP física por URL"),
    ("aquisição M2 por URL", "aquisição HTTP física por URL"),
    ("duration_ms do M2", "duration_ms da aquisição HTTP física"),
    ("Remediação de conteúdo/JSON-LD (M20)", "Remediação de conteúdo/JSON-LD"),
    ("Incompatíveis por timeout M23", "Incompatíveis por timeout da aquisição Synthetic Apdex"),
)

_SARI_STYLE = """
<style id='rasai-sari-visual-contract'>
.score-card.warn{background:var(--soft-amber)}
.score-card.good{background:var(--soft-green)}
.score-card.low{background:rgba(169,111,56,.08)}
.score-card.bad{background:var(--soft-red)}
.score-card.neutral{background:var(--soft-blue)}
</style>
"""


def install() -> None:
    """Install stricter benefit/degradation requirements before AI execution."""
    _install_improvement_contract()
    _install_content_remediation_contract()


def _install_improvement_contract() -> None:
    from rasai import improvement_intelligence as intelligence

    if getattr(intelligence, "_rasai_benefit_degradation_contract", False):
        return

    original_schema = intelligence._schema
    original_validate = intelligence._validate_ai_payload
    original_instructions = intelligence._instructions
    original_fingerprint = intelligence.ImprovementConfig.fingerprint

    def schema_with_impact(findings: list[dict[str, Any]], maximum: int) -> dict[str, Any]:
        schema = deepcopy(original_schema(findings, maximum))
        item = schema["properties"]["recommendations"]["items"]
        properties = item["properties"]
        properties["current_degradation"] = {
            "type": "string",
            "minLength": 1,
            "maxLength": 3000,
            "description": (
                "Evidence-bound current degradation, limitation or risk caused by the observed "
                "condition. Do not invent impact or claim causality not supported by evidence."
            ),
        }
        properties["expected_benefit"] = {
            "type": "string",
            "minLength": 1,
            "maxLength": 3000,
            "description": (
                "Evidence-bound qualitative benefit expected if the recommendation is applied. "
                "Do not promise ranking, traffic, revenue, conversion, or a numeric gain."
            ),
        }
        required = list(item["required"])
        for field in ("current_degradation", "expected_benefit"):
            if field not in required:
                required.append(field)
        item["required"] = required
        return schema

    def validate_with_impact(
        payload: Any,
        findings: list[dict[str, Any]],
        maximum: int,
    ) -> tuple[str, list[dict[str, Any]]]:
        normalized = payload
        if isinstance(payload, Mapping) and isinstance(payload.get("recommendations"), list):
            normalized = dict(payload)
            recommendations: list[Any] = []
            for raw in payload["recommendations"]:
                if not isinstance(raw, Mapping):
                    recommendations.append(raw)
                    continue
                item = dict(raw)
                degradation = str(item.pop("current_degradation", "") or "").strip()
                benefit = str(item.pop("expected_benefit", "") or "").strip()
                if not degradation or not benefit:
                    raise ValueError(
                        "Improvement Intelligence recommendation requires "
                        "current_degradation and expected_benefit"
                    )
                rationale = str(item.get("rationale") or "").strip()
                parts = [
                    "Degradação/risco atual: " + degradation,
                    "Benefício esperado se aplicado: " + benefit,
                ]
                if rationale:
                    parts.append("Justificativa técnica: " + rationale)
                item["rationale"] = "\n".join(parts)
                recommendations.append(item)
            normalized["recommendations"] = recommendations
        return original_validate(normalized, findings, maximum)

    def instructions_with_impact(language: str, domains: tuple[str, ...]) -> str:
        return (
            original_instructions(language, domains)
            + " For every recommendation, current_degradation and expected_benefit are mandatory. "
            "current_degradation must describe only the evidence-supported limitation/risk that exists now. "
            "expected_benefit must describe the qualitative improvement expected if applied. "
            "Never promise a ranking, traffic, revenue, conversion, security or performance outcome; "
            "state uncertainty when the evidence cannot support a stronger conclusion."
        )

    def fingerprint_with_impact_contract(config) -> str:
        base = original_fingerprint(config)
        return sha256((base + "|benefit-degradation-v1").encode("utf-8")).hexdigest()

    intelligence._schema = schema_with_impact
    intelligence._validate_ai_payload = validate_with_impact
    intelligence._instructions = instructions_with_impact
    intelligence.ImprovementConfig.fingerprint = fingerprint_with_impact_contract
    intelligence.CONTRACT_VERSION = IMPROVEMENT_CONTRACT_VERSION
    intelligence._rasai_benefit_degradation_contract = True


def _install_content_remediation_contract() -> None:
    from rasai import m20_ai

    if getattr(m20_ai, "_rasai_benefit_degradation_contract", False):
        return

    original_schema = m20_ai.content_remediation_schema
    original_validate = m20_ai._validate_response

    def schema_with_impact(request=None) -> dict[str, Any]:
        schema = deepcopy(original_schema(request))
        item = schema["properties"]["suggestions"]["items"]
        properties = item["properties"]
        properties["current_degradation"] = {
            "type": "string",
            "minLength": 1,
            "maxLength": 2000,
            "description": "Current evidence-supported content/semantic limitation caused by the finding.",
        }
        properties["expected_benefit"] = {
            "type": "string",
            "minLength": 1,
            "maxLength": 2000,
            "description": (
                "Qualitative evidence-bound benefit expected after applying the proposed text; "
                "do not promise ranking, traffic or conversion."
            ),
        }
        required = list(item["required"])
        for field in ("current_degradation", "expected_benefit"):
            if field not in required:
                required.append(field)
        item["required"] = required
        return schema

    def validate_with_impact(payload: Any, request):
        normalized = payload
        if isinstance(payload, Mapping) and isinstance(payload.get("suggestions"), list):
            normalized = dict(payload)
            suggestions: list[Any] = []
            for raw in payload["suggestions"]:
                if not isinstance(raw, Mapping):
                    suggestions.append(raw)
                    continue
                item = dict(raw)
                degradation = str(item.pop("current_degradation", "") or "").strip()
                benefit = str(item.pop("expected_benefit", "") or "").strip()
                if not degradation or not benefit:
                    raise m20_ai.ContentRemediationContractError(
                        "CONTENT_REMEDIATION_MISSING_IMPACT_EXPLANATION",
                        "content suggestion requires current degradation and expected benefit",
                    )
                review_note = str(item.get("review_note") or "").strip()
                parts = [
                    "Degradação/risco atual: " + degradation,
                    "Benefício esperado se aplicado: " + benefit,
                ]
                if review_note:
                    parts.append("Revisão humana: " + review_note)
                item["review_note"] = "\n".join(parts)
                suggestions.append(item)
            normalized["suggestions"] = suggestions
        return original_validate(normalized, request)

    m20_ai.content_remediation_schema = schema_with_impact
    m20_ai._validate_response = validate_with_impact

    # Some adapters import these symbols once at module import time.
    try:
        from rasai import provider_extensions_m20
    except ImportError:
        provider_extensions_m20 = None
    if provider_extensions_m20 is not None:
        provider_extensions_m20.content_remediation_schema = schema_with_impact
        provider_extensions_m20._validate_response = validate_with_impact
        original_extension_instructions = provider_extensions_m20._instructions

        def extension_instructions_with_impact() -> str:
            return (
                original_extension_instructions()
                + " For every suggestion, current_degradation and expected_benefit are mandatory, "
                "evidence-bound, qualitative and non-promissory."
            )

        provider_extensions_m20._instructions = extension_instructions_with_impact

    m20_ai._rasai_benefit_degradation_contract = True


def reconcile_public_report_quality(*, audit_id: str, workspace: AuditWorkspace) -> None:
    """Apply the final user-facing reconciliation after every late report enricher."""
    report_dir = workspace.root / "report"
    if not report_dir.is_dir():
        return

    connection = sqlite3.connect(workspace.database)
    connection.row_factory = sqlite3.Row
    try:
        overall_rows = _overall_rows(connection, audit_id)
        lighthouse_detail = _lighthouse_unavailable_detail(connection, audit_id)
        device_states = _device_states(connection, audit_id)
        gsc_state = _service_state(connection, audit_id, "google-search-console")
    finally:
        connection.close()

    for path in sorted(report_dir.glob("*.html")):
        try:
            html = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue

        html = _sanitize_owned_internal_tokens(html)
        html = normalize_owned_public_report_text(html)
        if path.name == "ai-usage.html":
            html = _add_ai_usage_sanitization_note(html)

        if path.name == "index.html" and lighthouse_detail:
            for title in (
                "Lighthouse Performance",
                "Lighthouse Accessibility",
                "Lighthouse Best Practices",
                "Lighthouse SEO técnico",
            ):
                html = _rewrite_indicator_detail(html, title, lighthouse_detail)

        if path.name == "scoring.html":
            html = _reconcile_sari_scoring_html(html, overall_rows)

        if path.name in {"index.html", "readiness.html", "scoring.html", "mobile.html", "desktop.html"}:
            html = _inject_sari_style(html)

        if path.name == "desktop.html" and "DESKTOP" not in device_states:
            html = _replace_generic_no_data(
                html,
                "Desktop não foi solicitado/materializado nesta auditoria; a execução possui "
                + (", ".join(sorted(device_states)) if device_states else "nenhum contexto de dispositivo persistido")
                + ". Ausência de Desktop não é falha do website.",
            )
        elif path.name == "mobile.html" and "MOBILE" not in device_states:
            html = _replace_generic_no_data(
                html,
                "Mobile não foi solicitado/materializado nesta auditoria. Ausência de Mobile não é falha do website.",
            )
        elif path.name == "ai-visibility.html":
            html = _replace_generic_no_data(
                html,
                "Nenhum dataset/import observacional de visibilidade generativa foi materializado nesta auditoria. "
                "Esta superfície é import-first e não chama LLM para fabricar observações.",
            )
        elif path.name == "observability.html":
            if gsc_state == "NOT_CONFIGURED":
                reason = (
                    "Nenhuma observação pós-auditoria foi materializada. Google Search Console foi solicitado, "
                    "mas não estava configurado; URL Inspection, CrUX History e imports continuam dependentes de "
                    "suas fontes/configurações próprias. Isso não é falha do website."
                )
            else:
                reason = (
                    "Nenhuma observação pós-auditoria foi materializada para as fontes configuradas nesta execução. "
                    "Isso não é convertido em falha do website."
                )
            html = _replace_generic_no_data(html, reason)
        elif path.name == "quality.html":
            html = _replace_generic_no_data(
                html,
                "Nenhuma execução de Quality / fix verification / evidence timeline foi materializada para esta auditoria. "
                "Esta superfície é preenchida pelo fluxo de Quality quando ele é executado; o estado vazio não reduz o SARI.",
            )

        try:
            path.write_text(html, encoding="utf-8", newline="\n")
        except OSError:
            continue


def _add_ai_usage_sanitization_note(html: str) -> str:
    marker = "data-public-identifier-sanitization='true'"
    if marker in html:
        return html
    notice = (
        "<div class='notice' data-public-identifier-sanitization='true'><strong>Identificadores públicos:</strong> "
        "nomes internos de etapas do RASAi são normalizados somente na projeção HTML. Quando um payload de transporte "
        "é exibido nesta página, o SHA-256 continua referindo-se ao conteúdo original persistido/enviado; a cópia visual "
        "pode substituir identificadores internos por nomes funcionais sem alterar audit.db ou a evidência bruta.</div>"
    )
    heading = "<h2>Log de comunicação com IA</h2>"
    if heading in html:
        return html.replace(heading, heading + notice, 1)
    return html


def _overall_rows(connection: sqlite3.Connection, audit_id: str) -> list[sqlite3.Row]:
    try:
        return list(
            connection.execute(
                "SELECT * FROM scores WHERE audit_id=? AND dimension='OVERALL_READINESS' ORDER BY device",
                (audit_id,),
            ).fetchall()
        )
    except sqlite3.Error:
        return []


def _device_states(connection: sqlite3.Connection, audit_id: str) -> set[str]:
    devices: set[str] = set()
    for sql in (
        "SELECT DISTINCT device FROM page_snapshots ps JOIN pages p ON p.page_id=ps.page_id WHERE p.audit_id=?",
        "SELECT DISTINCT device FROM scores WHERE audit_id=? AND device IS NOT NULL",
    ):
        try:
            rows = connection.execute(sql, (audit_id,)).fetchall()
        except sqlite3.Error:
            continue
        for row in rows:
            value = str(row[0] or "").strip().upper()
            if value:
                devices.add(value)
    return devices


def _service_state(connection: sqlite3.Connection, audit_id: str, service_id: str) -> str | None:
    try:
        row = connection.execute(
            "SELECT state FROM standards_service_runs WHERE audit_id=? AND service_id=? ORDER BY rowid DESC LIMIT 1",
            (audit_id, service_id),
        ).fetchone()
    except sqlite3.Error:
        return None
    return str(row[0]).upper() if row and row[0] is not None else None


def _lighthouse_unavailable_detail(connection: sqlite3.Connection, audit_id: str) -> str | None:
    try:
        rows = connection.execute(
            "SELECT status,http_status,duration_ms,error_code,error_message "
            "FROM web_performance_attempts WHERE audit_id=? AND UPPER(service) LIKE 'PAGESPEED%' "
            "ORDER BY created_at DESC,rowid DESC",
            (audit_id,),
        ).fetchall()
    except sqlite3.Error:
        return None
    if not rows:
        return None
    row = rows[0]
    if str(row["status"] or "").upper() == "SUCCESS":
        return None
    code = str(row["error_code"] or "ERRO_EXTERNO")
    message = str(row["error_message"] or "").strip()
    duration_ms = int(row["duration_ms"] or 0)
    seconds = max(1, round(duration_ms / 1000)) if duration_ms else None
    parts = [f"PageSpeed/Lighthouse não concluiu: {code}"]
    if seconds:
        parts.append(f"após {seconds}s")
    detail = " ".join(parts)
    if message:
        detail += f" ({message})"
    return (
        detail
        + ". Nenhuma categoria Lighthouse válida foi persistida; CrUX, quando disponível, permanece independente."
    )


def _rewrite_indicator_detail(html: str, title: str, detail: str) -> str:
    pattern = re.compile(
        r"(<article\b[^>]*\bindicator-card\b[^>]*>.*?<h3>"
        + re.escape(title)
        + r"</h3>.*?<span class=['\"]indicator-condition['\"]>.*?</span>\s*)"
        r"<p class=['\"]intro['\"]>.*?</p>",
        flags=re.IGNORECASE | re.DOTALL,
    )
    return pattern.sub(
        lambda match: match.group(1) + f"<p class='intro'>{escape(detail)}</p>",
        html,
        count=1,
    )


def _replace_generic_no_data(html: str, reason: str) -> str:
    replacement = "<strong>Motivo nesta execução:</strong> " + escape(reason)
    if _GENERIC_NO_DATA in html:
        return html.replace(_GENERIC_NO_DATA, replacement, 1)
    return html


def _inject_sari_style(html: str) -> str:
    if "rasai-sari-visual-contract" in html:
        return html
    return html.replace("</head>", _SARI_STYLE + "</head>", 1) if "</head>" in html else html


def _condition_state(condition: str) -> str:
    return {
        "expected": "good",
        "near": "warn",
        "below": "warn",
        "critical": "bad",
        "neutral": "neutral",
    }.get(condition, "neutral")


def _reconcile_sari_scoring_html(html: str, rows: Sequence[Any]) -> str:
    for row in rows:
        try:
            device = str(row["device"])
            value = row["value"]
        except (KeyError, IndexError, TypeError):
            continue
        rendered = "Indisponível" if value is None else f"{float(value):.1f}/100"
        condition, readiness_label, quality_label = public_readiness_condition(row)
        state = _condition_state(condition)
        pattern = re.compile(
            r"<tr(?P<attrs>[^>]*)>\s*<td>"
            + re.escape(device)
            + r"</td>\s*<td>(?P<score>"
            + re.escape(rendered)
            + r"(?:.*?))</td>(?P<tail>.*?)</tr>",
            flags=re.IGNORECASE | re.DOTALL,
        )

        def replace(match: re.Match[str]) -> str:
            attrs = re.sub(
                r"\sclass=(?P<q>['\"])(?P<classes>[^'\"]*)(?P=q)",
                lambda cm: _filtered_row_class(cm, condition, state),
                match.group("attrs"),
                count=1,
                flags=re.IGNORECASE,
            )
            if "class=" not in attrs:
                attrs += f" class='score-condition-{condition} result-state-{state}'"
            if "data-sari-overall=" not in attrs:
                attrs += " data-sari-overall='true'"
            score = re.sub(
                r"<span class=['\"]score-condition-tag\b.*?</span>",
                "",
                match.group("score"),
                flags=re.I | re.S,
            )
            score += (
                f" <span class='score-condition-tag {escape(condition, quote=True)}'>"
                f"{escape(readiness_label)}</span><br><small>Qualidade medida: {escape(quality_label)}</small>"
            )
            return f"<tr{attrs}><td>{escape(device)}</td><td>{score}</td>{match.group('tail')}</tr>"

        html = pattern.sub(replace, html, count=1)
    return html


def _filtered_row_class(match: re.Match[str], condition: str, state: str) -> str:
    classes = [
        item
        for item in match.group("classes").split()
        if not item.startswith("result-state-") and not item.startswith("score-condition-")
    ]
    classes.extend((f"score-condition-{condition}", f"result-state-{state}"))
    return f" class={match.group('q')}{' '.join(classes)}{match.group('q')}"


def _sanitize_owned_internal_tokens(html: str) -> str:
    """Normalize known RASAi delivery identifiers without touching arbitrary M25-like evidence."""
    for old, new in _OWNED_TOKEN_REPLACEMENTS:
        html = html.replace(old, new)
    html = html.replace("análise semântica M18", "análise semântica principal")
    html = html.replace("remediação textual M20", "remediação textual por IA")
    html = html.replace("Synthetic Apdex M23", "Synthetic Apdex")
    html = html.replace("Rastreamento e descoberta M24", "Rastreamento e descoberta")
    html = re.sub(r"\bM18_(?=[A-Z0-9_])", "SEMANTIC_ANALYSIS_", html)
    html = re.sub(r"\bM20_(?=[A-Z0-9_])", "CONTENT_REMEDIATION_", html)
    html = re.sub(r"\bM23_(?=[A-Z0-9_])", "SYNTHETIC_APDEX_", html)
    html = re.sub(r"\bM24_(?=[A-Z0-9_])", "CRAWLING_DISCOVERY_", html)
    return html
