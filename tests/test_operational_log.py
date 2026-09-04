from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from searchgeo.operational_log import append_operational_event, operational_log_path
from searchgeo.persistence import AuditWorkspace


class OperationalLogTests(unittest.TestCase):
    def test_sensitive_fields_are_redacted_and_configuration_booleans_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = AuditWorkspace(Path(directory) / "AUD-LOG")
            secret = "secret-value-must-not-appear"

            path = append_operational_event(
                workspace,
                "TEST_EVENT",
                api_key=secret,
                authorization=f"Bearer {secret}",
                nested={"access_token": secret, "safe": "visible"},
                pagespeed_api_key_configured=True,
                ordinary="value",
            )

            self.assertEqual(path, operational_log_path(workspace))
            payload = json.loads(path.read_text(encoding="utf-8").strip())
            self.assertEqual(payload["event"], "TEST_EVENT")
            self.assertEqual(payload["api_key"], "[REDACTED]")
            self.assertEqual(payload["authorization"], "[REDACTED]")
            self.assertEqual(payload["nested"]["access_token"], "[REDACTED]")
            self.assertEqual(payload["nested"]["safe"], "visible")
            self.assertTrue(payload["pagespeed_api_key_configured"])
            self.assertEqual(payload["ordinary"], "value")
            self.assertNotIn(secret, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
