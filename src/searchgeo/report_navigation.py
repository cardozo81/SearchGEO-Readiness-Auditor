"""Canonical navigation for the generated static report site.

All report pages must use the same ordered menu. Optional pages are included only
when their HTML file exists, and exactly the current page is marked as active.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import re


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

_NAV_ASIDE_RE = re.compile(
    r"<aside\b[^>]*>.*?<nav\b[^>]*>.*?</nav>.*?</aside>",
    flags=re.IGNORECASE | re.DOTALL,
)


def available_navigation(report_dir: Path) -> tuple[tuple[str, str], ...]:
    """Return canonical menu items whose target pages currently exist."""
    return tuple((label, filename) for label, filename in NAV_ITEMS if (report_dir / filename).is_file())


def render_report_navigation(report_dir: Path, current: str) -> str:
    """Render the canonical report menu with only ``current`` marked active."""
    links = available_navigation(report_dir)
    rendered = "".join(
        f"<a class='{'active' if filename == current else ''}' href='{escape(filename)}'>{escape(label)}</a>"
        for label, filename in links
    )
    return (
        "<aside class='app-nav' aria-label='Navegação do relatório'>"
        "<div class='brand'><small>SearchGEO Auditor</small><strong>Relatório da auditoria</strong></div>"
        f"<nav>{rendered}</nav></aside>"
    )


def normalize_report_navigation(report_dir: Path) -> None:
    """Rewrite every generated report page to the same canonical navigation."""
    for html_path in sorted(report_dir.glob("*.html")):
        html = html_path.read_text(encoding="utf-8")
        navigation = render_report_navigation(report_dir, html_path.name)
        normalized, replacements = _NAV_ASIDE_RE.subn(navigation, html, count=1)
        if replacements != 1:
            raise ValueError(f"report page has no replaceable navigation: {html_path}")
        html_path.write_text(normalized, encoding="utf-8", newline="\n")
