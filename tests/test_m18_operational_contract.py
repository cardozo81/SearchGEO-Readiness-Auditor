from __future__ import annotations

from pathlib import Path
import unittest

from searchgeo.m18_persistence import _resolve_session_status


class M18OperationalContractTests(unittest.TestCase):
    def test_single_provider_failure_is_degraded_not_chain_exhausted(self) -> None:
        status, exhausted = _resolve_session_status(
            strategy="SINGLE_PROVIDER",
            enabled=True,
            audit_mode="DEGRADED",
            provider_states={"OPENAI": "QUARANTINED_FOR_AUDIT"},
        )
        self.assertEqual(status, "DEGRADED")
        self.assertFalse(exhausted)

    def test_auto_all_quarantined_is_chain_exhausted(self) -> None:
        status, exhausted = _resolve_session_status(
            strategy="AUTO",
            enabled=True,
            audit_mode="DEGRADED",
            provider_states={
                "OPENAI": "QUARANTINED_FOR_AUDIT",
                "DEEPSEEK": "QUARANTINED_FOR_AUDIT",
            },
        )
        self.assertEqual(status, "CHAIN_EXHAUSTED")
        self.assertTrue(exhausted)

    def test_cli_reference_documents_every_exposed_argument(self) -> None:
        text = Path("docs/CLI_REFERENCE.md").read_text(encoding="utf-8")
        required_tokens = (
            "`-h`, `--help`",
            "`--version`",
            "`--config PATH`",
            "`target`",
            "`--urls-file PATH`",
            "`--project TEXT`",
            "`--language CODE`",
            "`--market CODE`",
            "`--max-pages N`",
            "`--audits-root PATH`",
            "`--ai-provider`",
            "`--ai-model MODEL_ID`",
        )
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, text)

        for provider in ("none", "openai", "deepseek", "mimo", "auto"):
            with self.subTest(provider=provider):
                self.assertIn(provider, text)


if __name__ == "__main__":
    unittest.main()
