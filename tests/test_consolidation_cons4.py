from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from rasai.consolidation.cons4 import REPORT_FORMAT_VERSION, find_existing, materialize, request_fingerprint
from rasai.consolidation.models import ConsolidationFilter, GenerationResult, RefreshResult


class Cons4MaterializationTests(unittest.TestCase):
    def test_reused_cons3_is_cloned_and_left_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "consolidated" / "CONS-LEGACY"
            legacy.mkdir(parents=True)
            report = legacy / "report.html"
            manifest = legacy / "manifest.json"
            report.write_text(
                "<html><section id='apdex'><p>legacy</p></section>"
                "<footer>Gerado em x · formato CONS-3 · fingerprint old</footer></html>",
                encoding="utf-8",
            )
            manifest.write_text(json.dumps({
                "cons_id": "CONS-LEGACY",
                "report_format_version": "CONS-3",
                "request_fingerprint": "old",
                "source_fingerprint": "source",
                "aggregation_policy": {},
            }), encoding="utf-8")
            report_before = report.read_bytes()
            manifest_before = manifest.read_bytes()
            refresh = RefreshResult(1, 0, 1, 0, ())
            base = GenerationResult(legacy, report, manifest, True, "old", refresh)

            result = materialize(
                audits_root=root,
                base_result=base,
                source_fingerprint="source",
                filters=ConsolidationFilter(),
                series=(),
            )

            self.assertNotEqual(result.report_dir, legacy)
            self.assertEqual(report.read_bytes(), report_before)
            self.assertEqual(manifest.read_bytes(), manifest_before)
            payload = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["report_format_version"], REPORT_FORMAT_VERSION)
            self.assertEqual(payload["request_fingerprint"], result.request_fingerprint)
            self.assertEqual(payload["temporal_apdex"]["contract"], "TEMPORAL-APDEX-001")
            self.assertIn("formato CONS-4", result.report_path.read_text(encoding="utf-8"))
            reused = find_existing(root, result.request_fingerprint, refresh)
            self.assertIsNotNone(reused)
            self.assertTrue(reused.reused)

    def test_new_base_snapshot_is_upgraded_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "consolidated" / "CONS-NEW"
            output.mkdir(parents=True)
            report = output / "report.html"
            manifest = output / "manifest.json"
            report.write_text(
                "<html><section id='apdex'><p>base</p></section>"
                "<footer>Gerado em x · formato CONS-3 · fingerprint base</footer></html>",
                encoding="utf-8",
            )
            manifest.write_text(json.dumps({
                "cons_id": "CONS-NEW",
                "report_format_version": "CONS-3",
                "request_fingerprint": "base",
                "source_fingerprint": "source",
                "aggregation_policy": {},
            }), encoding="utf-8")
            base = GenerationResult(output, report, manifest, False, "base", RefreshResult(1, 1, 0, 0, ()))
            result = materialize(
                audits_root=root,
                base_result=base,
                source_fingerprint="source",
                filters=ConsolidationFilter(),
                series=(),
            )
            self.assertEqual(result.report_dir, output)
            self.assertIn("formato CONS-4", report.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(manifest.read_text())["report_format_version"], "CONS-4")

    def test_request_fingerprint_is_stable_and_filter_sensitive(self) -> None:
        base = request_fingerprint("source", ConsolidationFilter())
        self.assertEqual(base, request_fingerprint("source", ConsolidationFilter()))
        self.assertNotEqual(base, request_fingerprint("other", ConsolidationFilter()))
        self.assertNotEqual(base, request_fingerprint("source", ConsolidationFilter(devices=("MOBILE",))))


if __name__ == "__main__":
    unittest.main()
