from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from searchgeo.console_config import (
    State,
    build_command,
    environment_summary,
    preflight,
    provider_capabilities,
    validate_env_value,
)


class InteractiveConsoleTests(unittest.TestCase):
    def test_defaults_are_single_url_mobile_without_ai(self) -> None:
        state = State()
        self.assertEqual(state.input_mode, "url")
        self.assertEqual(state.device, "mobile")
        self.assertEqual(state.ai_provider, "none")
        self.assertFalse(state.content_remediation)
        self.assertFalse(state.web_performance)

    def test_only_configured_valid_providers_are_available(self) -> None:
        caps = provider_capabilities({})
        self.assertTrue(caps["none"].available)
        self.assertFalse(caps["openai"].available)
        self.assertFalse(caps["deepseek"].available)
        self.assertFalse(caps["mimo"].available)
        self.assertFalse(caps["auto"].available)
        caps = provider_capabilities({"OPENAI_API_KEY": "sk-test"})
        self.assertTrue(caps["openai"].available)
        self.assertTrue(caps["auto"].available)

    def test_mimo_token_plan_key_is_rejected(self) -> None:
        caps = provider_capabilities({"MIMO_API_KEY": "tp-test"})
        self.assertFalse(caps["mimo"].available)
        with self.assertRaises(ValueError):
            validate_env_value("MIMO_API_KEY", "tp-test")

    def test_invalid_model_reasoning_and_runtime_quarantine_disable_provider(self) -> None:
        caps = provider_capabilities({"OPENAI_API_KEY": "sk-test", "SEARCHGEO_OPENAI_MODEL": "bad"})
        self.assertFalse(caps["openai"].available)
        caps = provider_capabilities({"OPENAI_API_KEY": "sk-test", "SEARCHGEO_OPENAI_REASONING_EFFORT": "bad"})
        self.assertFalse(caps["openai"].available)
        caps = provider_capabilities({"OPENAI_API_KEY": "sk-test"}, {"openai": "AUTH_ERROR/HTTP 401"})
        self.assertFalse(caps["openai"].available)
        self.assertFalse(caps["auto"].available)

    def test_environment_header_masks_secrets(self) -> None:
        values = environment_summary({"OPENAI_API_KEY": "secret-value", "SEARCHGEO_LOG_LEVEL": "DEBUG"})
        rendered = " | ".join(values)
        self.assertIn("OPENAI_API_KEY=[SET]", rendered)
        self.assertNotIn("secret-value", rendered)
        self.assertIn("SEARCHGEO_LOG_LEVEL=DEBUG", rendered)
        custom = " | ".join(environment_summary({"SEARCHGEO_CUSTOM_API_KEY": "also-secret"}))
        self.assertIn("SEARCHGEO_CUSTOM_API_KEY=[SET]", custom)
        self.assertNotIn("also-secret", custom)

    def test_preflight_accepts_single_url(self) -> None:
        state = State(target="https://example.com/path")
        self.assertEqual(preflight(state, {}), ("https://example.com/path",))

    def test_preflight_txt_validates_origin_and_max_pages(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "urls.txt"
            path.write_text("https://example.com/a\nhttps://example.com/b\n", encoding="utf-8")
            state = State(input_mode="file", target=str(path), max_pages=2)
            self.assertEqual(len(preflight(state, {})), 2)
            state.max_pages = 1
            with self.assertRaises(ValueError):
                preflight(state, {})
            path.write_text("https://example.com/a\nhttps://other.example/b\n", encoding="utf-8")
            state.max_pages = 2
            with self.assertRaises(ValueError):
                preflight(state, {})

    def test_preflight_blocks_incompatible_features_before_execution(self) -> None:
        state = State(target="https://example.com", content_remediation=True)
        with self.assertRaises(ValueError):
            preflight(state, {})
        state.content_remediation = False
        state.field_source = "crux"
        self.assertEqual(preflight(state, {}), ("https://example.com/",))
        state.web_performance = True
        with self.assertRaises(ValueError):
            preflight(state, {})

    def test_command_delegates_to_stable_audit_cli(self) -> None:
        state = State(
            target="https://example.com",
            project="Example",
            device="both",
            ai_provider="openai",
            ai_model="gpt-5.6-terra",
            content_remediation=True,
            web_performance=True,
            field_source="none",
        )
        command = build_command(state)
        self.assertIn("audit", command)
        self.assertIn("--device-context", command)
        self.assertIn("both", command)
        self.assertIn("--ai-provider", command)
        self.assertIn("openai", command)
        self.assertIn("--ai-content-remediation", command)
        self.assertIn("--web-performance", command)
        self.assertIn("--web-performance-field-source", command)
        self.assertIn("none", command)


if __name__ == "__main__":
    unittest.main()
