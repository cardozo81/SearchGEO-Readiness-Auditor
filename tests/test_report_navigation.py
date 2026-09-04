from __future__ import annotations

from pathlib import Path
import re
import tempfile
import unittest

from searchgeo.report_navigation import NAV_ITEMS, normalize_report_navigation


_LINK_RE = re.compile(r"<a class='([^']*)' href='([^']+)'>([^<]+)</a>")
_NAV_RE = re.compile(r"<nav>(.*?)</nav>", re.DOTALL)


class ReportNavigationTests(unittest.TestCase):
    def test_all_generated_pages_share_canonical_order_and_current_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp)
            filenames = [filename for _, filename in NAV_ITEMS]
            for index, filename in enumerate(filenames):
                old_links = "".join(f"<a href='{name}'>{name}</a>" for name in reversed(filenames[: index + 1]))
                (report_dir / filename).write_text(
                    f"<html><body><aside><nav>{old_links}</nav></aside><main>{filename}</main></body></html>",
                    encoding="utf-8",
                )

            normalize_report_navigation(report_dir)

            expected = [(filename, label) for label, filename in NAV_ITEMS]
            for filename in filenames:
                html = (report_dir / filename).read_text(encoding="utf-8")
                nav_match = _NAV_RE.search(html)
                self.assertIsNotNone(nav_match, filename)
                links = _LINK_RE.findall(nav_match.group(1))
                self.assertEqual([(href, label) for _, href, label in links], expected, filename)
                active = [href for css_class, href, _ in links if css_class == "active"]
                self.assertEqual(active, [filename], filename)

    def test_optional_pages_are_omitted_until_their_files_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp)
            for filename in ("index.html", "mobile.html", "remediation.html", "ai-usage.html", "references.html"):
                (report_dir / filename).write_text(
                    "<html><body><aside class='app-nav'><nav></nav></aside><main></main></body></html>",
                    encoding="utf-8",
                )

            normalize_report_navigation(report_dir)

            html = (report_dir / "index.html").read_text(encoding="utf-8")
            nav_match = _NAV_RE.search(html)
            self.assertIsNotNone(nav_match)
            hrefs = [href for _, href, _ in _LINK_RE.findall(nav_match.group(1))]
            self.assertEqual(
                hrefs,
                ["index.html", "mobile.html", "remediation.html", "ai-usage.html", "references.html"],
            )
            self.assertNotIn("desktop.html", hrefs)
            self.assertNotIn("content-suggestions.html", hrefs)
            self.assertNotIn("web-performance.html", hrefs)


if __name__ == "__main__":
    unittest.main()
