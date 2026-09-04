"""Pre-run integration exposure and post-run measured usage summaries."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sqlite3

from searchgeo.cli import validate_target
from searchgeo.console_config import DEFAULT_MODELS, MODEL_ENV, PROVIDERS, State, provider_capabilities
from searchgeo.m18_ai import PRICING_CATALOG
from searchgeo.url_utils import normalize_url


@dataclass(frozen=True, slots=True)
class ExposureEstimate:
    """Conservative pre-run exposure based only on known configuration."""

    level: str
    min_pages: int
    max_pages: int
    device_contexts: int
    min_ai_attempts: int
    max_ai_attempts: int
    min_web_calls: int
    max_web_calls: int
    pricing_lines: tuple[str, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ActualUsage:
    """Measured/persisted external usage for the completed audit."""

    ai_attempts: int
    ai_successes: int
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    total_tokens: int
    costs: tuple[tuple[str, float], ...]
    unpriced_ai_attempts: int
    web_external_calls: int
    web_services: tuple[tuple[str, int], ...]


def _configured_page_range(state: State) -> tuple[int, int]:
    if state.input_mode == "file":
        path = Path(state.target).expanduser()
        if not path.is_file():
            return 0, 0
        try:
            urls: list[str] = []
            for line in path.read_text(encoding="utf-8").splitlines():
                raw = line.strip()
                if not raw or raw.startswith("#"):
                    continue
                try:
                    urls.append(normalize_url(validate_target(raw)))
                except ValueError:
                    continue
        except (OSError, UnicodeError):
            return 0, 0
        count = len(dict.fromkeys(urls))
        # TXT is an explicit URL_SET; preflight blocks count > max-pages.
        return count, count
    if not state.target.strip() or state.max_pages <= 0:
        return 0, 0
    # A single URL is a crawl seed: one page is known and max-pages is the ceiling.
    return 1, state.max_pages


def _selected_provider_models(state: State) -> tuple[tuple[str, str], ...]:
    if state.ai_provider == "none":
        return ()
    if state.ai_provider in PROVIDERS:
        provider = PROVIDERS[state.ai_provider]
        model = state.ai_model or os.environ.get(MODEL_ENV[provider], DEFAULT_MODELS[provider])
        return ((provider, model),)
    if state.ai_provider == "auto":
        capabilities = provider_capabilities(blocks=state.runtime_blocks)
        rows: list[tuple[str, str]] = []
        for selection, provider in PROVIDERS.items():
            if capabilities.get(selection) and capabilities[selection].available:
                rows.append((provider, os.environ.get(MODEL_ENV[provider], DEFAULT_MODELS[provider])))
        return tuple(rows)
    return ()


def _pricing_lines(provider_models: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    lines: list[str] = []
    for provider, model in provider_models:
        prices = [item for item in PRICING_CATALOG if item.provider == provider and item.model == model]
        if not prices:
            lines.append(f"{provider}/{model}: preço unitário não catalogado; custo monetário prévio não estimável.")
            continue
        currencies = {item.currency for item in prices}
        if len(currencies) != 1:
            lines.append(f"{provider}/{model}: catálogo possui moedas distintas; custo prévio não consolidado.")
            continue
        currency = prices[0].currency
        input_values = sorted({item.input_price_per_million for item in prices})
        output_values = sorted({item.output_price_per_million for item in prices})
        input_text = f"{input_values[0]:g}" if len(input_values) == 1 else f"{input_values[0]:g}–{input_values[-1]:g}"
        output_text = f"{output_values[0]:g}" if len(output_values) == 1 else f"{output_values[0]:g}–{output_values[-1]:g}"
        lines.append(
            f"{provider}/{model}: input {currency} {input_text}/1M tokens; output {currency} {output_text}/1M tokens."
        )
    return tuple(lines)


def _model_price_weight(provider_models: tuple[tuple[str, str], ...]) -> int:
    """Internal qualitative weight; deliberately not a billing formula."""
    maximum_output = 0.0
    for provider, model in provider_models:
        prices = [item.output_price_per_million for item in PRICING_CATALOG if item.provider == provider and item.model == model]
        if prices:
            maximum_output = max(maximum_output, max(prices))
    if maximum_output <= 0:
        return 2 if provider_models else 0
    if maximum_output <= 1:
        return 1
    if maximum_output <= 5:
        return 2
    if maximum_output <= 15:
        return 3
    return 4


def estimate_exposure(state: State) -> ExposureEstimate:
    """Estimate request-volume exposure without inventing token quantities."""
    min_pages, max_pages = _configured_page_range(state)
    devices = 2 if state.device == "both" else 1
    provider_models = _selected_provider_models(state)
    provider_count = len(provider_models)

    min_ai = 0
    max_ai = 0
    if provider_count:
        # M18 is potentially one semantic context per materialized page/device.
        min_ai = min_pages * devices
        max_ai = max_pages * devices * provider_count
        # M20 is conditional on eligible findings, therefore contributes only to the ceiling.
        if state.content_remediation:
            max_ai += max_pages * devices * provider_count

    min_web = 0
    max_web = 0
    if state.web_performance:
        web_pages_min = min(min_pages, state.web_max_pages) if state.web_max_pages else min_pages
        web_pages_max = min(max_pages, state.web_max_pages) if state.web_max_pages else max_pages
        # Lighthouse/PageSpeed is the base external request. CrUX direct may add another request.
        min_per_context = 1
        max_per_context = 2 if state.field_source in {"auto", "crux"} else 1
        min_web = web_pages_min * devices * min_per_context
        max_web = web_pages_max * devices * max_per_context

    reasons: list[str] = []
    if state.input_mode == "file" and min_pages:
        reasons.append(f"TXT contém {min_pages} URL(s) única(s) válida(s) conhecidas antes da execução.")
    elif max_pages:
        reasons.append(f"URL única é seed de crawl: 1 página conhecida, teto configurado de {max_pages}.")
    if devices == 2:
        reasons.append("BOTH duplica os contextos potenciais mobile/desktop.")
    if provider_count:
        reasons.append(
            f"IA ativa: até {max_ai} tentativa(s) potenciais considerando M18, cadeia de providers e M20 quando habilitado."
        )
    if state.content_remediation:
        reasons.append("M20 pode acrescentar tentativas apenas quando houver findings elegíveis.")
    if state.web_performance:
        reasons.append(f"M21: entre {min_web} e {max_web} chamada(s) externas potenciais PageSpeed/CrUX.")

    if not provider_count:
        # Google integrations are tracked as quota/external consumption; no monetary price is assumed here.
        level = "NENHUM"
    else:
        weight = _model_price_weight(provider_models)
        score = max_ai * max(weight, 1)
        if score <= 10:
            level = "BAIXO"
        elif score <= 50:
            level = "MÉDIO"
        elif score <= 200:
            level = "ALTO"
        else:
            level = "EXCESSIVO"
        reasons.append(
            "Faixa financeira é um índice interno de exposição baseado em volume máximo de tentativas e faixa de preço do modelo; não é invoice."
        )

    return ExposureEstimate(
        level=level,
        min_pages=min_pages,
        max_pages=max_pages,
        device_contexts=devices,
        min_ai_attempts=min_ai,
        max_ai_attempts=max_ai,
        min_web_calls=min_web,
        max_web_calls=max_web,
        pricing_lines=_pricing_lines(provider_models),
        reasons=tuple(reasons),
    )


def _table_exists(connection: sqlite3.Connection, table: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table,)
    ).fetchone()
    return row is not None


def _usage_from_table(connection: sqlite3.Connection, table: str) -> dict[str, int | float | dict[str, float]]:
    if not _table_exists(connection, table):
        return {
            "attempts": 0, "successes": 0, "input": 0, "cached": 0, "output": 0,
            "reasoning": 0, "total": 0, "unpriced": 0, "costs": {},
        }
    row = connection.execute(
        f"""
        SELECT COUNT(*) attempts,
               SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) successes,
               COALESCE(SUM(input_tokens),0) input_tokens,
               COALESCE(SUM(cached_input_tokens),0) cached_input_tokens,
               COALESCE(SUM(output_tokens),0) output_tokens,
               COALESCE(SUM(reasoning_tokens),0) reasoning_tokens,
               COALESCE(SUM(COALESCE(total_tokens, COALESCE(input_tokens,0)+COALESCE(output_tokens,0))),0) total_tokens,
               SUM(CASE WHEN estimated_cost IS NULL AND (input_tokens IS NOT NULL OR output_tokens IS NOT NULL) THEN 1 ELSE 0 END) unpriced
        FROM {table}
        """
    ).fetchone()
    costs = {
        str(currency): float(amount)
        for currency, amount in connection.execute(
            f"""
            SELECT cost_currency,COALESCE(SUM(estimated_cost),0)
            FROM {table}
            WHERE estimated_cost IS NOT NULL AND cost_currency IS NOT NULL
            GROUP BY cost_currency ORDER BY cost_currency
            """
        ).fetchall()
    }
    return {
        "attempts": int(row[0] or 0), "successes": int(row[1] or 0), "input": int(row[2] or 0),
        "cached": int(row[3] or 0), "output": int(row[4] or 0), "reasoning": int(row[5] or 0),
        "total": int(row[6] or 0), "unpriced": int(row[7] or 0), "costs": costs,
    }


def _web_usage(workspace: Path) -> tuple[int, tuple[tuple[str, int], ...]]:
    log_path = workspace / "logs" / "audit.log"
    if not log_path.is_file():
        return 0, ()
    services: dict[str, int] = {}
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return 0, ()
    for line in lines:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict) or payload.get("event") != "M21_EXTERNAL_ATTEMPT":
            continue
        service = str(payload.get("service") or "EXTERNAL").upper()
        services[service] = services.get(service, 0) + 1
    ordered = tuple(sorted(services.items()))
    return sum(count for _, count in ordered), ordered


def actual_usage(workspace: Path | None) -> ActualUsage | None:
    if workspace is None:
        return None
    database = workspace / "audit.db"
    if not database.is_file():
        return None
    try:
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True, timeout=0.5)
        try:
            m18 = _usage_from_table(connection, "ai_provider_attempts")
            m20 = _usage_from_table(connection, "content_remediation_attempts")
        finally:
            connection.close()
    except sqlite3.Error:
        return None

    costs: dict[str, float] = {}
    for source in (m18["costs"], m20["costs"]):
        assert isinstance(source, dict)
        for currency, amount in source.items():
            costs[str(currency)] = costs.get(str(currency), 0.0) + float(amount)
    web_calls, services = _web_usage(workspace)
    return ActualUsage(
        ai_attempts=int(m18["attempts"]) + int(m20["attempts"]),
        ai_successes=int(m18["successes"]) + int(m20["successes"]),
        input_tokens=int(m18["input"]) + int(m20["input"]),
        cached_input_tokens=int(m18["cached"]) + int(m20["cached"]),
        output_tokens=int(m18["output"]) + int(m20["output"]),
        reasoning_tokens=int(m18["reasoning"]) + int(m20["reasoning"]),
        total_tokens=int(m18["total"]) + int(m20["total"]),
        costs=tuple(sorted((currency, round(amount, 10)) for currency, amount in costs.items())),
        unpriced_ai_attempts=int(m18["unpriced"]) + int(m20["unpriced"]),
        web_external_calls=web_calls,
        web_services=services,
    )
