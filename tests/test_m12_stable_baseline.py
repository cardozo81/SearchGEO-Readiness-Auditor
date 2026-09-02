"""M12 critical end-to-end tests for the stable local baseline."""

from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch

from searchgeo.acquisition import HttpClient
from searchgeo.audit_runner import AuditRunResult, run_audit
from searchgeo.cli import main
from searchgeo.discovery import DiscoveryEngine
from searchgeo.domain import AuditMode, AuditStatus, CompletionStatus, DeviceContext
from searchgeo.persistence import AuditPersistence, AuditWorkspace
from searchgeo.rendering import BrowserRenderResult
from searchgeo.semantic import NoneProvider


class _BaselineHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        origin = f"http://127.0.0.1:{self.server.server_port}"
        if self.path == "/robots.txt":
            self._respond(200, "text/plain; charset=utf-8", f"User-agent: *\nAllow: /\nSitemap: {origin}/sitemap.xml\n".encode())
            return
        if self.path == "/sitemap.xml":
            body = f"<?xml version='1.0'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'><url><loc>{origin}/</loc></url><url><loc>{origin}/extra</loc></url></urlset>"
            self._respond(200, "application/xml", body.encode())
            return
        if self.path == "/":
            html = f"""<!doctype html><html lang='pt-BR'><head>
<title>Guia SearchGEO</title><meta name='description' content='Guia técnico.'>
<link rel='canonical' href='{origin}/'><script type='application/ld+json'>{{"@context":"https://schema.org","@type":"Article","headline":"Guia SearchGEO"}}</script>
</head><body><header><nav><a href='/extra'>Conteúdo adicional</a></nav></header>
<main><h1>Guia SearchGEO</h1><h2>Visão geral</h2><p>Este guia apresenta uma explicação técnica verificável sobre readiness para busca e sistemas generativos.</p><p>Publicado em 2026-09-02 pela Equipe Exemplo.</p></main></body></html>"""
            self._respond(200, "text/html; charset=utf-8", html.encode())
            return
        if self.path == "/extra":
            self._respond(200, "text/html; charset=utf-8", b"<html><head><title>Extra</title></head><body><main><h1>Extra</h1><p>Conteudo secundario.</p></main></body></html>")
            return
        self._respond(404, "text/plain", b"missing")

    def _respond(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


@contextmanager
def _server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _BaselineHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


class _FixtureRenderer:
    def __init__(self, html: str) -> None:
        self.html = html

    def render(self, url: str, device: DeviceContext) -> BrowserRenderResult:
        return BrowserRenderResult(
            requested_url=url,
            final_url=url,
            http_status=200,
            content_type="text/html; charset=utf-8",
            rendered_html=self.html,
            browser_metadata={
                "engine": "m12-fixture",
                "profile": {
                    "device": device.value,
                    "is_mobile": device is DeviceContext.MOBILE,
                    "has_touch": device is DeviceContext.MOBILE,
                },
                "render_error": None,
            },
        )


class M12StableBaselineTests(unittest.TestCase):
    def test_end_to_end_pipeline_materializes_all_rules_devices_scores_and_report(self) -> None:
        with _server() as origin, TemporaryDirectory() as directory:
            html = f"""<!doctype html><html lang='pt-BR'><head><title>Guia SearchGEO</title>
<meta name='description' content='Guia técnico.'><link rel='canonical' href='{origin}/'>
<script type='application/ld+json'>{{"@context":"https://schema.org","@type":"Article","headline":"Guia SearchGEO"}}</script>
</head><body><nav><a href='{origin}/extra'>Extra</a></nav><main><h1>Guia SearchGEO</h1><h2>Visão geral</h2><p>Conteúdo principal técnico e verificável para a auditoria.</p><p>Publicado em 2026-09-02 pela Equipe Exemplo.</p></main></body></html>"""
            result = run_audit(
                f"{origin}/",
                audits_root=Path(directory),
                project_name="Baseline M12",
                language="pt-BR",
                market="BR",
                max_pages=1,
                semantic_provider=NoneProvider(),
                discovery_engine=DiscoveryEngine(HttpClient(timeout=1)),
                renderer=_FixtureRenderer(html),
                lazy_probe=lambda url, device: None,
            )

            self.assertTrue(result.report_path.is_file())
            self.assertTrue((result.audit_root / "audit.db").is_file())
            self.assertTrue((result.audit_root / "artifacts").is_dir())
            self.assertEqual(result.audited_pages, 1)
            self.assertEqual(result.completion_status, CompletionStatus.COMPLETE_WITH_LIMITATIONS)

            workspace = AuditWorkspace.open(result.audit_root)
            with AuditPersistence(workspace) as persistence:
                audit = persistence.audits.get(result.audit_id)
                self.assertIsNotNone(audit)
                assert audit is not None
                self.assertEqual(audit.status, AuditStatus.COMPLETED)
                self.assertEqual(audit.completion_status, CompletionStatus.COMPLETE_WITH_LIMITATIONS)
                self.assertEqual(audit.audit_mode, AuditMode.NO_AI)
                self.assertTrue(
                    any(limitation.startswith("MAX_PAGES_REACHED:") for limitation in audit.limitations)
                )

            connection = sqlite3.connect(result.audit_root / "audit.db")
            connection.row_factory = sqlite3.Row
            try:
                rule_ids = {
                    row[0]
                    for row in connection.execute(
                        "SELECT DISTINCT rule_id FROM rule_executions WHERE audit_id = ?",
                        (result.audit_id,),
                    )
                }
                expected_rules = {f"BR-GEO-{number:03d}" for number in range(1, 55)}
                self.assertTrue(expected_rules.issubset(rule_ids), sorted(expected_rules - rule_ids))

                snapshots = connection.execute(
                    "SELECT device, COUNT(*) FROM page_snapshots GROUP BY device ORDER BY device"
                ).fetchall()
                self.assertEqual({row[0]: row[1] for row in snapshots}, {"DESKTOP": 1, "MOBILE": 1})

                score_devices = {
                    row[0]
                    for row in connection.execute("SELECT DISTINCT device FROM scores")
                }
                self.assertEqual(score_devices, {"DESKTOP", "MOBILE"})
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM reports").fetchone()[0], 1)

                invalid_findings = connection.execute(
                    """
                    SELECT COUNT(*) FROM findings
                    WHERE rule_execution_id IS NULL OR evidence_ids IS NULL OR evidence_ids = '[]'
                    """
                ).fetchone()[0]
                self.assertEqual(invalid_findings, 0)
            finally:
                connection.close()

            report = result.report_path.read_text(encoding="utf-8")
            self.assertIn('lang="pt-BR"', report)
            self.assertIn("Como interpretar este relatório", report)
            self.assertIn("Desktop", report)
            self.assertIn("Mobile", report)
            self.assertIn("Algumas avaliações semânticas não foram executadas", report)

    def test_cli_audit_command_delegates_to_full_runner_and_reports_paths(self) -> None:
        with TemporaryDirectory() as directory:
            expected = AuditRunResult(
                audit_id="AUD-TEST",
                audit_root=Path(directory) / "AUD-TEST",
                report_path=Path(directory) / "AUD-TEST" / "report.html",
                completion_status=CompletionStatus.COMPLETE_WITH_LIMITATIONS,
                audited_pages=2,
                finding_count=3,
                recommendation_count=2,
            )
            output = StringIO()
            with patch("searchgeo.cli.run_audit", return_value=expected) as mocked, redirect_stdout(output):
                exit_code = main([
                    "audit",
                    "example.com",
                    "--project",
                    "Projeto CLI",
                    "--max-pages",
                    "2",
                    "--audits-root",
                    directory,
                ])
            self.assertEqual(exit_code, 0)
            mocked.assert_called_once()
            _, kwargs = mocked.call_args
            self.assertEqual(kwargs["project_name"], "Projeto CLI")
            self.assertEqual(kwargs["max_pages"], 2)
            self.assertIsInstance(kwargs["semantic_provider"], NoneProvider)
            rendered = output.getvalue()
            self.assertIn("Auditoria concluída: AUD-TEST", rendered)
            self.assertIn("report.html", rendered)


if __name__ == "__main__":
    unittest.main()
