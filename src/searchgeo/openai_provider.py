"""Hardened OpenAI Responses API adapter for SearchGEO semantic analysis.

This module deliberately wraps the original provider contract rather than changing
M7 scoring/fallback semantics.  It adds four operational guarantees:

* the prompt carries the actual meaning of BR-GEO-028..049;
* Structured Outputs requests exactly one assessment for every semantic rule;
* normalized output is rejected unless all 22 rule ids are present once;
* HTTP failures retain a sanitized status/type/code/request-id diagnostic.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import HTTPError, URLError

from searchgeo.semantic import (
    OpenAIProvider as _BaseOpenAIProvider,
    ProviderCallResult,
    ProviderState,
    SEMANTIC_RULE_IDS,
    SemanticEvidenceError,
    SemanticInput,
    SemanticProviderError,
    SemanticSchemaError,
    _extract_json_payload,
    normalize_provider_payload,
    semantic_output_schema,
)


SEMANTIC_RULE_CRITERIA: dict[str, str] = {
    "BR-GEO-028": "title is present and semantically representative of the page",
    "BR-GEO-029": "main content exposes an understandable semantic hierarchy",
    "BR-GEO-030": "primary topic and major sections are identifiable with sufficient confidence",
    "BR-GEO-031": "primary entity is identifiable when applicable",
    "BR-GEO-032": "important entity types and relationships have sufficient context",
    "BR-GEO-033": "material entity ambiguity is absent or explicitly identifiable",
    "BR-GEO-034": "Structured Data is syntactically interpretable when present",
    "BR-GEO-035": "Structured Data types and relevant properties are identifiable",
    "BR-GEO-036": "Structured Data remains consistent with visible page content",
    "BR-GEO-037": "Structured Data entities remain consistent with observed page entities",
    "BR-GEO-038": "primary user intent is identifiable with evidence",
    "BR-GEO-039": "relevant primary questions receive explicit answers when applicable",
    "BR-GEO-040": "answers contain sufficient context",
    "BR-GEO-041": "material factual claims are explicitly identifiable",
    "BR-GEO-042": "factual statements contain sufficient factual context",
    "BR-GEO-043": "numeric, temporal and quantitative claims contain necessary qualifiers",
    "BR-GEO-044": "important information is understandable without excessive inference",
    "BR-GEO-045": "material claims expose appropriate attribution or support when required",
    "BR-GEO-046": "publisher, author or responsible entity is identifiable when relevant",
    "BR-GEO-047": "publication and freshness signals are internally consistent",
    "BR-GEO-048": "one primary and up to five relevant secondary intents are represented",
    "BR-GEO-049": "material intent coverage gaps are evidence-backed",
}

if tuple(SEMANTIC_RULE_CRITERIA) != SEMANTIC_RULE_IDS:
    raise RuntimeError("semantic rule criteria must cover BR-GEO-028..049 in canonical order")

_SAFE_DIAGNOSTIC_TOKEN = re.compile(r"[^A-Za-z0-9_.-]+")


def hardened_semantic_output_schema() -> dict[str, Any]:
    """Return the strict semantic schema with a complete 22-rule assessment set."""

    schema = json.loads(json.dumps(semantic_output_schema()))
    assessments = schema["properties"]["assessments"]
    assessments["minItems"] = len(SEMANTIC_RULE_IDS)
    assessments["maxItems"] = len(SEMANTIC_RULE_IDS)
    return schema


class OpenAIProvider(_BaseOpenAIProvider):
    """Production CLI adapter with complete-rule and diagnostic hardening."""

    def analyze(self, semantic_input: SemanticInput) -> ProviderCallResult:
        if not self.api_key:
            return ProviderCallResult(ProviderState.NOT_CONFIGURED, reason="AI_NOT_CONFIGURED")

        body = json.dumps(self._request_payload(semantic_input), ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            raw = self._transport(self.endpoint, headers, body, self.timeout)
        except HTTPError as exc:
            return ProviderCallResult(
                ProviderState.UNAVAILABLE,
                reason=_http_error_reason(exc),
            )
        except (URLError, TimeoutError, OSError) as exc:
            return ProviderCallResult(
                ProviderState.UNAVAILABLE,
                reason=f"AI_PROVIDER_UNAVAILABLE:{type(exc).__name__}",
            )

        try:
            payload = _extract_json_payload(raw)
            normalized = normalize_provider_payload(
                payload,
                semantic_input.allowed_evidence_ids,
                provider=self.name,
                model=self.model,
                configuration_version=self.configuration_version,
                prompt_id=self.prompt_id,
                prompt_version=self.prompt_version,
            )
        except (
            SemanticProviderError,
            SemanticSchemaError,
            SemanticEvidenceError,
            json.JSONDecodeError,
            UnicodeError,
            TypeError,
            ValueError,
        ) as exc:
            return ProviderCallResult(
                ProviderState.UNAVAILABLE,
                reason=f"AI_PROVIDER_UNAVAILABLE:{type(exc).__name__}",
            )

        received = tuple(item.rule_id for item in normalized.assessments)
        if len(received) != len(SEMANTIC_RULE_IDS) or frozenset(received) != frozenset(SEMANTIC_RULE_IDS):
            return ProviderCallResult(
                ProviderState.UNAVAILABLE,
                reason="AI_PROVIDER_UNAVAILABLE:INCOMPLETE_SEMANTIC_OUTPUT",
            )

        return ProviderCallResult(ProviderState.AVAILABLE, response=normalized)

    def _request_payload(self, semantic_input: SemanticInput) -> dict[str, Any]:
        criteria = "\n".join(
            f"- {rule_id}: {SEMANTIC_RULE_CRITERIA[rule_id]}"
            for rule_id in SEMANTIC_RULE_IDS
        )
        instructions = (
            "Evaluate only the supplied page evidence for Search/GEO readiness. "
            "Return JSON matching the strict schema. Never invent evidence_ids or hidden facts. "
            "Do not score the website. Use UNKNOWN when evidence is insufficient and "
            "NOT_APPLICABLE only when the rule genuinely does not apply. "
            "The assessments array MUST contain exactly one item for every rule listed below, "
            "with no omissions and no duplicates.\n\nSemantic rule contract:\n"
            + criteria
        )
        return {
            "model": self.model,
            "instructions": instructions,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "JSON page evidence:\n"
                            + json.dumps(semantic_input.provider_payload(), ensure_ascii=False),
                        }
                    ],
                }
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "searchgeo_semantic_assessment",
                    "strict": True,
                    "schema": hardened_semantic_output_schema(),
                }
            },
        }


def _http_error_reason(exc: HTTPError) -> str:
    """Create a bounded diagnostic without storing response messages or credentials."""

    error_type = None
    error_code = None
    try:
        raw = exc.read(65536)
        decoded = json.loads(raw.decode("utf-8", errors="replace"))
        error = decoded.get("error") if isinstance(decoded, dict) else None
        if isinstance(error, dict):
            error_type = _safe_token(error.get("type"))
            error_code = _safe_token(error.get("code"))
    except (OSError, UnicodeError, json.JSONDecodeError, AttributeError, TypeError, ValueError):
        pass

    request_id = None
    try:
        if exc.headers is not None:
            request_id = _safe_token(exc.headers.get("x-request-id"))
    except (AttributeError, TypeError):
        request_id = None

    parts = ["AI_PROVIDER_UNAVAILABLE", f"HTTP_{int(exc.code)}"]
    if error_type:
        parts.append(f"type={error_type}")
    if error_code:
        parts.append(f"code={error_code}")
    if request_id:
        parts.append(f"request_id={request_id}")
    return ":".join(parts)


def _safe_token(value: Any) -> str | None:
    if value is None:
        return None
    token = _SAFE_DIAGNOSTIC_TOKEN.sub("_", str(value).strip())[:96].strip("_")
    return token or None
