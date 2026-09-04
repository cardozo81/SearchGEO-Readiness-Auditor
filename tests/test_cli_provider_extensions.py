from __future__ import annotations

import unittest

from searchgeo.cli import build_parser as legacy_build_parser
from searchgeo.cli_extensions import build_parser


class CLIProviderExtensionTests(unittest.TestCase):
    def test_extension_cli_adds_only_explicit_provider_choices(self) -> None:
        parser = build_parser()
        args = parser.parse_args([
            "audit", "https://example.com", "--ai-provider", "xai",
        ])
        self.assertEqual(args.ai_provider, "xai")

        for provider in ("grok", "qwen", "gemini", "anthropic", "claude"):
            with self.subTest(provider=provider):
                parsed = parser.parse_args([
                    "audit", "https://example.com", "--ai-provider", provider,
                ])
                self.assertEqual(parsed.ai_provider, provider)

    def test_legacy_parser_surface_is_not_mutated(self) -> None:
        parser = legacy_build_parser()
        subparsers = next(
            action
            for action in parser._actions
            if getattr(action, "choices", None) and "audit" in action.choices
        )
        audit_parser = subparsers.choices["audit"]
        ai_action = next(action for action in audit_parser._actions if action.dest == "ai_provider")
        self.assertEqual(tuple(ai_action.choices), ("none", "openai", "deepseek", "mimo", "auto"))

    def test_auto_remains_an_available_legacy_choice(self) -> None:
        parser = build_parser()
        args = parser.parse_args([
            "audit", "https://example.com", "--ai-provider", "auto",
        ])
        self.assertEqual(args.ai_provider, "auto")


if __name__ == "__main__":
    unittest.main()
