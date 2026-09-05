"""Static HTML snapshot generation for consolidated historical reports."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from html import escape
from pathlib import Path
import hashlib
import json

from .models import ConsolidatedData, GenerationResult, NumericSummary, RefreshResult

REPORT_FORMAT_VERSION = "CONS-1"


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _request_fingerprint(data: ConsolidatedData) -> str:
    payload = {
        "report_format_version": REPORT_FORMAT_VERSION,
        "filters": data.filters.canonical(),
        "source_fingerprint": data.source_fingerprint,
    }
    return hashlib.sha256(_json(payload).encode("utf-8")).hexdigest()


def _find_existing(root: Path, fingerprint: str) -> tuple[Path, Path] | None:
    output_root = root / "consolidated"
    if not output_root.is_dir():
        return None
    for manifest in sorted(output_root.glob("CONS-*/manifest.json"), reverse=True):
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("request_fingerprint") != fingerprint:
            continue
        report = manifest.parent / "report.html"
        if report.is_file():
            return report, manifest
    return None


def _fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def _stats_cells(stats: NumericSummary, *, coverage: float | None = None) -> str:
    return (
        f"<td>{stats.count}</td><td>{_fmt(stats.initial)}</td><td>{_fmt(stats.current)}</td>"
        f"<td>{_fmt(stats.mean)}</td><td>{_fmt(stats.median)}</td><td>{_fmt(stats.minimum)}</td>"
        f"<td>{_fmt(stats.maximum)}</td><td>{_fmt(stats.change_absolute)}</td>"
        f"<td>{_fmt(stats.change_percent)}%</td><td>{_pct(coverage)}</td>"
    )


def _render_scores(data: ConsolidatedData) -> str:
    if not data.scores:
        return "<section><h2>Compatibilidade GEO</h2><p class='empty'>Nenhum score comparável persistido para o filtro.</p></section>"
    rows: list[str] = []
    notes: list[str] = []
    for item in data.scores:
        rows.append(
            "<tr>"
            f"<td>{escape(item.device)}</td><td>{escape(item.dimension)}</td>"
            f"<td>{escape(', '.join(item.scoring_versions))}</td>"
            + _stats_cells(item.statistics, coverage=item.average_coverage)
            + f"<td>{escape(_json(item.confidence_counts))}</td>"
            f"<td>{escape(_json(item.consolidation_counts))}</td></tr>"
        )
        if item.limitation:
            notes.append(f"<li><strong>{escape(item.device)} / {escape(item.dimension)}:</strong> {escape(item.limitation)}</li>")
    note_html = f"<ul class='notes'>{''.join(notes)}</ul>" if notes else ""
    return f"""
    <section id='scores'><h2>Compatibilidade GEO e dimensões</h2>
    <p>Valores são resumidos apenas dentro de versões metodologicamente compatíveis. Ausência de dado não é convertida em zero.</p>
    <div class='table-wrap'><table><thead><tr><th>Device</th><th>Dimensão</th><th>Scoring version</th><th>N</th><th>Inicial</th><th>Atual</th><th>Média</th><th>Mediana</th><th>Mín</th><th>Máx</th><th>Δ abs.</th><th>Δ %</th><th>Coverage média</th><th>Confidence</th><th>Consolidação</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>{note_html}</section>
    """


def _render_performance(data: ConsolidatedData) -> str:
    if not data.performance:
        return "<section><h2>Web Performance</h2><p class='empty'>Nenhuma observação Web Performance persistida para o filtro.</p></section>"
    blocks: list[str] = []
    for item in data.performance:
        metric_rows = "".join(
            "<tr>"
            f"<td>{escape(metric.name)}</td><td>{escape(metric.unit)}</td>"
            + _stats_cells(metric.statistics)
            + "</tr>"
            for metric in item.metrics
        )
        blocks.append(f"""
        <article class='panel'><h3>{escape(item.device)}</h3>
        <div class='metric-grid'><div><small>Observações</small><strong>{item.observations}</strong></div><div><small>URLs</small><strong>{item.urls}</strong></div><div><small>CWV</small><strong>{escape(_json(item.cwv_counts))}</strong></div><div><small>Fonte / escopo</small><strong>{escape(_json(item.source_scopes))}</strong></div></div>
        <div class='table-wrap'><table><thead><tr><th>Métrica</th><th>Unidade</th><th>N</th><th>Inicial</th><th>Atual</th><th>Média</th><th>Mediana</th><th>Mín</th><th>Máx</th><th>Δ abs.</th><th>Δ %</th><th>Coverage</th></tr></thead><tbody>{metric_rows}</tbody></table></div></article>
        """)
    return "<section id='performance'><h2>Web Performance</h2><p>Lab e field data permanecem identificados por suas métricas e pela origem/escopo persistidos; não são tratados como equivalentes.</p>" + "".join(blocks) + "</section>"


def _render_apdex(data: ConsolidatedData) -> str:
    if not data.apdex:
        return "<section><h2>Synthetic Apdex</h2><p class='empty'>Nenhum resumo Synthetic Apdex persistido para o filtro.</p></section>"
    blocks: list[str] = []
    for item in data.apdex:
        rows = "".join(
            "<tr>"
            f"<td>{escape(metric.name)}</td><td>{escape(metric.unit)}</td>"
            + _stats_cells(metric.statistics)
            + "</tr>"
            for metric in item.duration_metrics
        )
        limitation = f"<p class='notice'>{escape(item.limitation)}</p>" if item.limitation else ""
        blocks.append(f"""
        <article class='panel'><h3>{escape(item.device)}</h3>
        <div class='metric-grid'><div><small>Apdex ponderado por amostra válida</small><strong>{_fmt(item.weighted_apdex, 3)}</strong></div><div><small>Amostras válidas</small><strong>{item.valid_samples}</strong></div><div><small>Inválidas</small><strong>{item.invalid_samples}</strong></div><div><small>URLs</small><strong>{item.urls}</strong></div><div><small>Perfis</small><strong>{escape(', '.join(item.profile_ids))}</strong></div><div><small>Thresholds</small><strong>{escape(', '.join(_fmt(value, 3) for value in item.thresholds))}</strong></div><div><small>Grupos small</small><strong>{item.small_groups}</strong></div><div><small>Grupos finais</small><strong>{item.final_groups}</strong></div></div>
        {limitation}
        <div class='table-wrap'><table><thead><tr><th>Métrica</th><th>Unidade</th><th>N</th><th>Inicial</th><th>Atual</th><th>Média</th><th>Mediana</th><th>Mín</th><th>Máx</th><th>Δ abs.</th><th>Δ %</th><th>Coverage</th></tr></thead><tbody>{rows}</tbody></table></div></article>
        """)
    return "<section id='apdex'><h2>Synthetic Apdex</h2><p>Agregação somente entre perfil e threshold compatíveis; o score consolidado é ponderado pelo número de amostras válidas.</p>" + "".join(blocks) + "</section>"


def _render_findings(data: ConsolidatedData) -> str:
    finding = data.findings
    return f"""
    <section id='findings'><h2>Ocorrências persistidas</h2>
    <p>Contagens servem como estatística histórica; não alteram nem recalculam o SCORE GEO.</p>
    <div class='metric-grid'><div><small>Findings</small><strong>{finding.observations}</strong></div><div><small>Páginas afetadas</small><strong>{finding.affected_pages}</strong></div><div><small>Severidades</small><strong>{escape(_json(finding.severity_counts))}</strong></div><div><small>Categorias</small><strong>{escape(_json(finding.category_counts))}</strong></div></div></section>
    """


def _render_audits(data: ConsolidatedData) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{escape(str(row.get('audit_id') or ''))}</td>"
        f"<td>{escape(str(row.get('event_time') or ''))}</td>"
        f"<td>{escape(str(row.get('project_name') or ''))}</td>"
        f"<td>{escape(str(row.get('auditor_version') or ''))}</td>"
        f"<td>{escape(str(row.get('ruleset_version') or ''))}</td>"
        f"<td>{escape(str(row.get('devices_json') or ''))}</td>"
        f"<td>{int(row.get('url_count') or 0)}</td></tr>"
        for row in data.audits
    )
    return f"""
    <section id='sources'><h2>Auditorias consideradas</h2>
    <div class='table-wrap'><table><thead><tr><th>Audit ID</th><th>Data efetiva</th><th>Projeto</th><th>Auditor</th><th>Ruleset</th><th>Devices</th><th>URLs</th></tr></thead><tbody>{rows}</tbody></table></div></section>
    """


def _render_html(data: ConsolidatedData, generated_at: str, request_fingerprint: str) -> str:
    filters = data.filters.canonical()
    limitations = "".join(f"<li>{escape(item)}</li>" for item in data.limitations) or "<li>Nenhuma limitação adicional registrada pelo consolidador.</li>"
    return f"""<!doctype html>
<html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>SearchGEO — Relatório Consolidado</title>
<style>
:root{{--bg:#f6f7fb;--surface:#fffefd;--ink:#273449;--muted:#6f7b8d;--line:rgba(111,123,141,.16);--blue:#657fc6;--green:#5f9674;--amber:#b68a50;--red:#bf6f70;--soft:#eef2fb}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14.5px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}header{{background:#2f3a4d;color:white;padding:22px 28px}}header h1{{margin:0;font-size:1.55rem}}header p{{margin:.35rem 0 0;color:#d8e0ea}}main{{max-width:1500px;margin:auto;padding:28px}}section,.panel{{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:20px;margin:0 0 18px;box-shadow:0 3px 12px rgba(47,58,78,.035)}}.panel{{margin-top:14px}}h2{{margin-top:0}}.metric-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}}.metric-grid>div{{background:#f7f8fb;border-radius:5px;padding:12px}}small{{display:block;color:var(--muted);margin-bottom:5px}}strong{{overflow-wrap:anywhere}}.table-wrap{{overflow:auto;margin-top:12px}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:9px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:#f2f4f8;position:sticky;top:0}}.notice{{background:#fbf4e8;border-left:4px solid var(--amber);padding:10px 12px}}.empty{{color:var(--muted)}}.notes{{padding-left:20px}}code{{word-break:break-all}}footer{{color:var(--muted);padding:0 4px 30px}}
</style></head><body>
<header><h1>SearchGEO — Relatório Consolidado</h1><p>Snapshot estático, offline e reproduzível de indicadores persistidos.</p></header>
<main>
<section><h2>Escopo</h2><div class='metric-grid'>
<div><small>Auditorias</small><strong>{len(data.audits)}</strong></div><div><small>URLs únicas</small><strong>{data.unique_urls}</strong></div>
<div><small>Primeira observação</small><strong>{escape(data.date_min or '—')}</strong></div><div><small>Última observação</small><strong>{escape(data.date_max or '—')}</strong></div>
<div><small>Domínios</small><strong>{escape(', '.join(filters['domains']) or 'todos')}</strong></div><div><small>Devices</small><strong>{escape(', '.join(filters['devices']) or 'todos')}</strong></div>
<div><small>Período solicitado</small><strong>{escape(str(filters['date_from'] or 'início'))} → {escape(str(filters['date_to'] or 'fim'))}</strong></div><div><small>URLs filtradas</small><strong>{len(filters['urls']) if filters['urls'] else 'todas'}</strong></div>
</div></section>
{_render_scores(data)}
{_render_performance(data)}
{_render_apdex(data)}
{_render_findings(data)}
<section id='method'><h2>Metodologia e limitações</h2><ul>{limitations}</ul><p>Fonte de verdade: <code>AUD-*/audit.db</code>. O índice analítico é cache derivado e pode ser apagado/reconstruído. Nenhuma API é chamada na consolidação e nenhum <code>audit.db</code> é escrito.</p></section>
{_render_audits(data)}
<footer>Gerado em {escape(generated_at)} · formato {REPORT_FORMAT_VERSION} · fingerprint {escape(request_fingerprint)}</footer>
</main></body></html>"""


def write_report(*, audits_root: Path, data: ConsolidatedData, refresh: RefreshResult) -> GenerationResult:
    fingerprint = _request_fingerprint(data)
    existing = _find_existing(audits_root, fingerprint)
    if existing is not None:
        report_path, manifest_path = existing
        return GenerationResult(
            report_dir=report_path.parent,
            report_path=report_path,
            manifest_path=manifest_path,
            reused=True,
            request_fingerprint=fingerprint,
            refresh=refresh,
        )

    now = datetime.now().astimezone()
    cons_id = now.strftime("CONS-%Y%m%d-%H%M%S-%f")[:-3]
    output = audits_root / "consolidated" / cons_id
    output.mkdir(parents=True, exist_ok=False)
    generated_at = now.isoformat()
    report_path = output / "report.html"
    manifest_path = output / "manifest.json"
    manifest = {
        "cons_id": cons_id,
        "report_format_version": REPORT_FORMAT_VERSION,
        "generated_at": generated_at,
        "request_fingerprint": fingerprint,
        "source_fingerprint": data.source_fingerprint,
        "filters": data.filters.canonical(),
        "summary": {
            "audits": len(data.audits),
            "unique_urls": data.unique_urls,
            "date_min": data.date_min,
            "date_max": data.date_max,
        },
        "source_audits": [
            {
                "audit_id": row.get("audit_id"),
                "db_path": row.get("db_path"),
                "source_fingerprint": row.get("source_fingerprint"),
                "event_time": row.get("event_time"),
                "auditor_version": row.get("auditor_version"),
                "ruleset_version": row.get("ruleset_version"),
            }
            for row in data.audits
        ],
        "limitations": list(data.limitations),
        "refresh": {
            "discovered": refresh.discovered,
            "indexed": refresh.indexed,
            "reused": refresh.reused,
            "removed": refresh.removed,
            "issues": [asdict(item) for item in refresh.issues],
        },
    }
    report_path.write_text(_render_html(data, generated_at, fingerprint), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return GenerationResult(
        report_dir=output,
        report_path=report_path,
        manifest_path=manifest_path,
        reused=False,
        request_fingerprint=fingerprint,
        refresh=refresh,
    )
