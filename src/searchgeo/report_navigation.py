"""Canonical navigation for the generated static report site.

All report pages must use the same ordered menu. Optional pages are included only
when their HTML file exists, and exactly the current page is marked as active.
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from searchgeo import __version__


NAV_ITEMS: tuple[tuple[str, str], ...] = (
    ("Visão geral", "index.html"),
    ("Relatório Mobile", "mobile.html"),
    ("Relatório Desktop", "desktop.html"),
    ("Remediações", "remediation.html"),
    ("Conteúdo e JSON-LD", "content-suggestions.html"),
    ("Web Performance", "web-performance.html"),
    ("Uso de IA", "ai-usage.html"),
    ("Referências e metodologia", "references.html"),
)

BRASILIA_TIMEZONE = ZoneInfo("America/Sao_Paulo")

_NAV_ASIDE_RE = re.compile(
    r"<aside\b[^>]*>.*?<nav\b[^>]*>.*?</nav>.*?</aside>",
    flags=re.IGNORECASE | re.DOTALL,
)


def available_navigation(report_dir: Path, current: str | None = None) -> tuple[tuple[str, str], ...]:
    """Return canonical menu items available in the current report projection."""
    return tuple(
        (label, filename)
        for label, filename in NAV_ITEMS
        if (report_dir / filename).is_file() or filename == current
    )


def format_report_generated_at(generated_at: datetime | None = None) -> str:
    """Return the report generation timestamp in Brasília time."""
    instant = generated_at or datetime.now(BRASILIA_TIMEZONE)
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=BRASILIA_TIMEZONE)
    else:
        instant = instant.astimezone(BRASILIA_TIMEZONE)
    return instant.strftime("%d/%m/%Y %H:%M:%S")


def render_report_navigation(
    report_dir: Path,
    current: str,
    *,
    generated_at: datetime | None = None,
    software_version: str | None = None,
) -> str:
    """Render the canonical report menu with version, timestamp and active item."""
    links = available_navigation(report_dir, current)
    rendered = "".join(
        f"<a class='{'active' if filename == current else ''}' href='{escape(filename)}'>{escape(label)}</a>"
        for label, filename in links
    )
    version = software_version or __version__
    generated_label = format_report_generated_at(generated_at)
    return (
        "<aside class='app-nav' aria-label='Navegação do relatório'>"
        "<div class='brand'>"
        "<small>SearchGEO Auditor</small>"
        "<strong>Relatório da auditoria</strong>"
        f"<small>Versão {escape(version)}</small>"
        f"<small>Gerado em {escape(generated_label)} — Horário de Brasília</small>"
        "</div>"
        f"<nav>{rendered}</nav></aside>"
    )


def normalize_report_navigation(
    report_dir: Path,
    *,
    generated_at: datetime | None = None,
    software_version: str | None = None,
) -> None:
    """Rewrite every generated page with one canonical menu and one final timestamp."""
    final_generated_at = generated_at or datetime.now(BRASILIA_TIMEZONE)
    version = software_version or __version__
    for html_path in sorted(report_dir.glob("*.html")):
        html = html_path.read_text(encoding="utf-8")
        navigation = render_report_navigation(
            report_dir,
            html_path.name,
            generated_at=final_generated_at,
            software_version=version,
        )
        normalized, replacements = _NAV_ASIDE_RE.subn(navigation, html, count=1)
        if replacements != 1:
            raise ValueError(f"report page has no replaceable navigation: {html_path}")
        html_path.write_text(normalized, encoding="utf-8", newline="\n")
