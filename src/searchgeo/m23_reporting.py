"""M23 report projection for Synthetic Navigation Apdex and Lighthouse traceability."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from html import escape
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

from searchgeo.persistence import AuditWorkspace
from searchgeo.report_navigation import normalize_report_navigation

_START = "<!-- searchgeo-m23-start -->"
_END = "<!-- searchgeo-m23-end -->"
_INDEX_START = "<!-- searchgeo-m23-index-start -->"
_INDEX_END = "<!-- searchgeo-m23-index-end -->"
_REF_START = "<!-- searchgeo-m23-references-start -->"
_REF_END = "<!-- searchgeo-m23-references-end -->"

_APDEX_SPEC = "https://www.apdex.org/wp-content/uploads/2020/09/ApdexTechnicalSpecificationV11_000.pdf"
_CDP_CPU = "https://chromedevtools.github.io/devtools-protocol/tot/Emulation/#method-setCPUThrottlingRate"
_CDP_NETWORK = "https://chromedevtools.github.io/devtools-protocol/tot/Network/"
_LIGHTHOUSE_RESULTS = "https://github.com/GoogleChrome/lighthouse/blob/main/docs/understanding-results.md"
_LIGHTHOUSE_EMULATION = "https://github.com/GoogleChrome/lighthouse/blob/main/docs/emulation.md"


def enrich_m23_report_site(*, audit_id: str, workspace: AuditWorkspace) -> Path:
    """Add M23 to the Web Performance domain without touching GEO scoring."""
    report_dir = workspace.root / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    data = _load(audit_id, workspace)
    performance_path = report_dir / "web-performance.html"
    if performance_path.is_file():
        html = performance_path.read_text(encoding="utf-8")
    else:
        html = (
            "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Web Performance — SearchGEO Readiness Auditor</title>"
            "<link rel='stylesheet' href='css/site.css'></head><body>"
            "<main class='app-main'><header class='hero'><div class='eyebrow'>"
            "Domínio Web Performance</div><h1>Web Performance</h1></header></main></body></html>\n"
        )
    html = _replace_or_insert(html, _START, _END, _m23_section(data), before="</main>")
    performance_path.write_text(html, encoding="utf-8", newline="\n")

    index_path = report_dir / "index.html"
    if index_path.is_file():
        index_html = index_path.read_text(encoding="utf-8")
        index_html = _replace_or_insert(
            index_html, _INDEX_START, _INDEX_END, _index_section(data), before="</main>"
        )
        index_path.write_text(index_html, encoding="utf-8", newline="\n")

    references_path = report_dir / "references.html"
    if references_path.is_file():
        references_html = references_path.read_text(encoding="utf-8")
        references_html = _replace_or_insert(
            references_html, _REF_START, _REF_END, _references_section(), before="</main>"
        )
        references_path.write_text(references_html, encoding="utf-8", newline="\n")

    normalize_report_navigation(report_dir)
    return performance_path


def _load(audit_id: str, workspace: AuditWorkspace) -> dict[str, Any]:
    connection = sqlite3.connect(workspace.database)
    connection.row_factory = sqlite3.Row
    try:
        return {
            "run": _one(connection, "SELECT * FROM synthetic_apdex_runs WHERE audit_id=?", (audit_id,)),
            "summaries": _many(
                connection,
                "SELECT * FROM synthetic_apdex_summaries WHERE audit_id=? ORDER BY url,device,summary_id",
                (audit_id,),
            ),
            "invalid_samples": _many(
                connection,
                """
                SELECT * FROM synthetic_apdex_samples
                WHERE audit_id=? AND classification IS NULL
                ORDER BY url,device,run_index,sample_id
                """,
                (audit_id,),
            ),
            "profiles": _many(
                connection,
                """
                SELECT * FROM lighthouse_execution_profiles
                WHERE audit_id=? ORDER BY url,device,observation_id
                """,
                (audit_id,),
            ),
        }
    finally:
        connection.close()


def _one(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> sqlite3.Row | None:
    try:
        return connection.execute(sql, params).fetchone()
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower():
            return None
        raise


def _many(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
    try:
        return list(connection.execute(sql, params).fetchall())
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower():
            return []
        raise


def _m23_section(data: dict[str, Any]) -> str:
    run = data["run"]
    summaries = data["summaries"]
    profiles = data["profiles"]
    invalid = data["invalid_samples"]
    enabled = bool(run["enabled"]) if run is not None else False
    status = str(run["status"]) if run is not None else "UNAVAILABLE"
    threshold = float(run["threshold_seconds"]) if run is not None and run["threshold_seconds"] is not None else None
    configuration = _json_object(run["configuration"]) if run is not None else {}
    host = _json_object(run["host_environment"]) if run is not None else {}

    if not enabled:
        apdex_notice = (
            "<div class='notice'><strong>Synthetic Navigation Apdex: NÃO CALCULADO.</strong> "
            "M23 está desabilitado. Nenhuma navegação sintética adicional é executada e nenhum "
            "threshold T é inventado.</div>"
        )
    elif status in {"UNAVAILABLE", "NO_CONTEXTS"}:
        apdex_notice = (
            "<div class='notice warn'><strong>Synthetic Navigation Apdex indisponível.</strong> "
            "A configuração estava ativa, mas não houve população válida suficiente para cálculo. "
            "Falha de ferramenta/perfil não é transformada em falha do website.</div>"
        )
    elif status == "PARTIAL":
        apdex_notice = (
            "<div class='notice warn'><strong>Coleta Apdex parcial.</strong> Algumas amostras foram "
            "excluídas por falha da ferramenta/perfil; as amostras válidas permanecem calculáveis.</div>"
        )
    else:
        apdex_notice = (
            "<div class='notice good'><strong>Synthetic Navigation Apdex coletado.</strong> "
            "O índice usa somente os tempos da Task NAVIGATION_LOAD sob T explícito e o perfil "
            "sintético declarado abaixo.</div>"
        )

    cards = "".join(_summary_card(row, configuration) for row in summaries)
    if not cards:
        cards = "<p class='intro'>Nenhum grupo de amostras Apdex calculável foi persistido.</p>"

    invalid_rows = "".join(
        "<tr>"
        f"<td class='mono'>{escape(str(row['url']))}</td>"
        f"<td>{escape(str(row['device']).upper())}</td>"
        f"<td>{int(row['run_index'])}</td>"
        f"<td>{escape(str(row['status']))}</td>"
        f"<td>{escape(str(row['error_code'] or '—'))}</td>"
        "</tr>"
        for row in invalid
    )

    lighthouse_rows = "".join(_lighthouse_row(row) for row in profiles)
    if not lighthouse_rows:
        lighthouse_rows = "<tr><td colspan='10'>Nenhum configSettings Lighthouse persistido disponível.</td></tr>"

    host_label = " · ".join(
        part for part in (
            str(host.get("system") or ""),
            str(host.get("release") or ""),
            f"Chromium {host.get('chromium_version')}" if host.get("chromium_version") else "",
            f"Playwright {host.get('playwright_version')}" if host.get("playwright_version") else "",
        ) if part
    ) or "não disponível"

    threshold_label = _format_t(threshold) if threshold is not None else "—"
    run_metrics = (
        _metric("Estado M23", status)
        + _metric("T", f"{threshold_label} s" if threshold is not None else "NÃO DEFINIDO")
        + _metric("F", f"{_format_t(4.0 * threshold)} s" if threshold is not None else "—")
        + _metric("Amostras válidas", int(run["valid_samples"]) if run is not None else 0)
        + _metric("Amostras excluídas", int(run["invalid_samples"]) if run is not None else 0)
        + _metric("Execuções/contexto", int(run["runs_per_context"]) if run is not None else 0)
    )

    return (
        f"{_START}<section id='m23-apdex' class='panel'>"
        "<div class='kicker'>M23 · domínio Web Performance</div>"
        "<h2>Synthetic Navigation Apdex</h2>"
        "<p class='intro'>Apdex não é derivado de Lighthouse, LCP, INP, CLS, TBT ou da latência "
        "da API PageSpeed. O SearchGEO mede repetidamente uma Task sintética explícita: do início de "
        "<code>page.goto</code> até a conclusão de <code>wait_until=load</code>, em contexto frio e "
        "perfil CPU/rede declarado.</p>"
        f"<div class='metric-grid'>{run_metrics}</div>{apdex_notice}"
        "<div class='notice'><strong>Regra Apdex:</strong> Satisfied ≤ T · Tolerating &gt; T e ≤ 4T · "
        "Frustrated &gt; 4T. Erro da aplicação/servidor detectável (por exemplo HTTP 404) é Frustrated. "
        "Falha da ferramenta ao aplicar o perfil é excluída da população e exibida separadamente.</div>"
        "<div class='notice'><strong>Tamanho da amostra:</strong> grupos com 1–99 amostras válidas "
        "recebem <code>*</code>; 100+ é o mínimo para relatório normal segundo a especificação Apdex. "
        "O valor exibido usa duas casas e sempre mostra T.</div>"
        f"{cards}"
        "<h3>Amostras excluídas por integridade da medição</h3>"
        "<p class='intro'>Essas ocorrências não entram no denominador. Uma indisponibilidade do "
        "browser/CDP/perfil não deve ser confundida com frustração causada pelo website.</p>"
        "<div class='table-wrap'><table><thead><tr><th>URL</th><th>Device</th><th>Run</th>"
        "<th>Status</th><th>Erro</th></tr></thead><tbody>"
        + (invalid_rows or "<tr><td colspan='5'>Nenhuma amostra inválida.</td></tr>")
        + "</tbody></table></div>"
        "<h3>Ambiente do executor sintético</h3>"
        f"<p class='intro'>{escape(host_label)}</p>"
        "</section>"
        "<section id='m23-lighthouse-traceability' class='panel'>"
        "<div class='kicker'>M23 · rastreabilidade de laboratório</div>"
        "<h2>Configuração efetiva do Lighthouse</h2>"
        "<p class='intro'>Os valores abaixo são extraídos do <code>lighthouseResult.configSettings</code> "
        "já persistido pelo M21. O SearchGEO não os inventa e não presume que o perfil Synthetic Apdex "
        "seja idêntico ao perfil Lighthouse. Campos ausentes permanecem como não informados.</p>"
        "<div class='table-wrap'><table><thead><tr><th>URL</th><th>Device</th><th>Form factor</th>"
        "<th>Throttling</th><th>RTT</th><th>Throughput</th><th>CPU</th><th>Viewport</th>"
        "<th>Benchmark</th><th>Tempo LH</th></tr></thead><tbody>"
        + lighthouse_rows
        + "</tbody></table></div>"
        "<p class='intro'><strong>Importante:</strong> o tempo total do Lighthouse é telemetria da "
        "execução do auditor Lighthouse, não é tempo de resposta Apdex e nunca entra na fórmula.</p>"
        "</section>"
        f"{_END}"
    )


def _summary_card(row: sqlite3.Row, configuration: dict[str, Any]) -> str:
    score = float(row["apdex_score"]) if row["apdex_score"] is not None else None
    threshold = float(row["threshold_seconds"])
    small = bool(row["small_group"])
    output = _uniform_apdex(score, threshold, small)
    rating = _rating(score)
    device = str(row["device"])
    profile = configuration.get("mobile_profile" if device == "mobile" else "desktop_profile")
    profile = profile if isinstance(profile, dict) else {}
    viewport = profile.get("viewport") if isinstance(profile.get("viewport"), dict) else {}
    profile_text = (
        f"{profile.get('profile_id', row['profile_id'])} · CPU {profile.get('cpu_slowdown', '—')}× · "
        f"RTT {profile.get('rtt_ms', '—')} ms · down {profile.get('download_kbps', '—')} Kbps · "
        f"up {profile.get('upload_kbps', '—')} Kbps · viewport "
        f"{viewport.get('width', '—')}×{viewport.get('height', '—')} · cache COLD_CONTEXT"
    )
    sample_note = (
        "Grupo pequeno: resultado diagnóstico, marcado obrigatoriamente com *."
        if small and int(row["valid_samples"]) > 0
        else "Grupo com 100+ amostras: apto ao formato normal de relatório Apdex."
        if int(row["valid_samples"]) >= 100
        else "Sem amostras válidas."
    )
    return (
        "<article class='page-card'>"
        "<div class='finding-head'><div>"
        f"<span class='badge'>{escape(device.upper())}</span> "
        f"<span class='badge info'>{escape(rating)}</span></div>"
        f"<span class='badge'>{escape(str(row['task_id']))}</span></div>"
        f"<h3 class='page-url'>{escape(str(row['url']))}</h3>"
        f"<div class='metric-grid'>{_metric('Apdex', output)}"
        f"{_metric('Satisfied', int(row['satisfied_count']))}"
        f"{_metric('Tolerating', int(row['tolerating_count']))}"
        f"{_metric('Frustrated', int(row['frustrated_count']))}"
        f"{_metric('Válidas', int(row['valid_samples']))}"
        f"{_metric('Excluídas', int(row['invalid_samples']))}</div>"
        f"<p class='intro'>{escape(sample_note)}</p>"
        f"<p class='intro'><strong>Perfil:</strong> {escape(profile_text)}</p>"
        f"<p class='intro'><strong>Distribuição temporal:</strong> mediana {_ms(row['median_ms'])} · "
        f"p75 {_ms(row['p75_ms'])} · p95 {_ms(row['p95_ms'])}.</p>"
        "</article>"
    )


def _lighthouse_row(row: sqlite3.Row) -> str:
    viewport = (
        f"{row['screen_width']}×{row['screen_height']} @ {row['device_scale_factor']}"
        if row["screen_width"] is not None and row["screen_height"] is not None
        else "—"
    )
    return (
        "<tr>"
        f"<td class='mono'>{escape(str(row['url']))}</td>"
        f"<td>{escape(str(row['device']).upper())}</td>"
        f"<td>{escape(str(row['form_factor'] or '—'))}</td>"
        f"<td>{escape(str(row['throttling_method'] or '—'))}</td>"
        f"<td>{_number(row['rtt_ms'], ' ms')}</td>"
        f"<td>{_number(row['throughput_kbps'], ' Kbps')}</td>"
        f"<td>{_number(row['cpu_slowdown_multiplier'], '×')}</td>"
        f"<td>{escape(viewport)}</td>"
        f"<td>{_number(row['benchmark_index'])}</td>"
        f"<td>{_number(row['lighthouse_total_ms'], ' ms')}</td>"
        "</tr>"
    )


def _index_section(data: dict[str, Any]) -> str:
    run = data["run"]
    summaries = data["summaries"]
    if run is None:
        state = "NÃO MATERIALIZADO"
        detail = "M23 ainda não possui estado persistido para esta auditoria."
    elif not bool(run["enabled"]):
        state = "DESABILITADO"
        detail = "Nenhuma navegação sintética adicional foi executada."
    else:
        state = str(run["status"])
        detail = f"{int(run['valid_samples'])} amostra(s) válida(s); T={_format_t(float(run['threshold_seconds']))} s."
    values = [float(row["apdex_score"]) for row in summaries if row["apdex_score"] is not None]
    best = max(values) if values else None
    best_label = f"{best:.2f}" if best is not None else "NÃO CALCULADO"
    return (
        f"{_INDEX_START}<section id='m23-apdex-summary' class='panel'>"
        "<div class='kicker'>Web Performance · M23</div><h2>Synthetic Navigation Apdex</h2>"
        "<p class='intro'>Indicador separado do SCORE-GEO-002. T é definido pelo operador e cada "
        "URL/dispositivo constitui seu próprio grupo de amostras.</p>"
        f"<div class='metric-grid'>{_metric('Estado', state)}{_metric('Melhor grupo', best_label)}"
        f"{_metric('Contextos com resultado', len(values))}</div>"
        f"<p class='intro'>{escape(detail)}</p>"
        "<p><a href='web-performance.html#m23-apdex'>Abrir Apdex e perfis de laboratório →</a></p>"
        f"</section>{_INDEX_END}"
    )


def _references_section() -> str:
    refs = (
        ("Apdex Technical Specification v1.1", _APDEX_SPEC, "Fórmula, T/F, exceções, tamanho de amostra e formato de apresentação."),
        ("Chrome DevTools Protocol — CPU throttling", _CDP_CPU, "Define o slowdown factor usado pela emulação de CPU do executor sintético."),
        ("Chrome DevTools Protocol — Network", _CDP_NETWORK, "Define emulação de latência/throughput e o fallback legado."),
        ("Lighthouse — understanding results", _LIGHTHOUSE_RESULTS, "Documenta configSettings e metadados efetivos do Lighthouse Result."),
        ("Lighthouse — emulation", _LIGHTHOUSE_EMULATION, "Distingue emulação de viewport/UA de throttling de CPU/rede."),
    )
    rows = "".join(
        "<tr>"
        f"<td>{escape(name)}</td><td>OFICIAL</td><td>{escape(use)}</td>"
        f"<td><a href='{escape(url)}' target='_blank' rel='noopener'>abrir fonte</a></td>"
        "</tr>"
        for name, url, use in refs
    )
    return (
        f"{_REF_START}<section id='m23-apdex-methodology' class='panel'>"
        "<div class='kicker'>M23 · metodologia</div><h2>Apdex sintético e rastreabilidade Lighthouse</h2>"
        "<p class='intro'>Estas fontes sustentam somente o domínio Web Performance. Não homologam "
        "SCORE-GEO-002 e não transformam métricas de laboratório em probabilidade de citação.</p>"
        "<div class='table-wrap'><table><thead><tr><th>Fonte</th><th>Base</th><th>Uso</th><th>Referência</th>"
        f"</tr></thead><tbody>{rows}</tbody></table></div></section>{_REF_END}"
    )


def _uniform_apdex(score: float | None, threshold: float, small: bool) -> str:
    t = _format_t(threshold)
    if score is None:
        return f"NS [{t}]"
    rounded = Decimal(str(score)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{rounded:.2f} [{t}]{'*' if small else ''}"


def _format_t(value: float) -> str:
    if value < 10:
        return f"{value:.1f}"
    if value < 1000:
        return f"{value:.0f}"
    return f"{value:.15g}"


def _rating(score: float | None) -> str:
    if score is None:
        return "NoSample"
    if score >= 0.94:
        return "Excellent"
    if score >= 0.85:
        return "Good"
    if score >= 0.70:
        return "Fair"
    if score >= 0.50:
        return "Poor"
    return "Unacceptable"


def _metric(label: str, value: Any) -> str:
    return f"<div class='metric'><small>{escape(str(label))}</small><strong>{escape(str(value))}</strong></div>"


def _ms(value: Any) -> str:
    return "—" if value is None else f"{float(value):.0f} ms"


def _number(value: Any, suffix: str = "") -> str:
    if value is None:
        return "—"
    number = float(value)
    shown = f"{number:.2f}".rstrip("0").rstrip(".")
    return escape(shown + suffix)


def _json_object(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _replace_or_insert(html: str, start: str, end: str, content: str, *, before: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), flags=re.DOTALL)
    if pattern.search(html):
        return pattern.sub(content, html, count=1)
    if before in html:
        return html.replace(before, content + before, 1)
    return html + content
