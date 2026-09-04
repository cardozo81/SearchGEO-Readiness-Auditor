"""CLI shim that exposes additive AI providers without modifying the legacy CLI core."""

from __future__ import annotations

from typing import Sequence

from searchgeo import cli as _legacy_cli
from searchgeo import m20 as _m20
from searchgeo.provider_extensions import build_semantic_provider
from searchgeo.provider_extensions_m20 import build_content_remediation_router

_EXTENSION_CHOICES = ("xai", "grok", "qwen", "gemini", "anthropic", "claude")


def build_parser():
    """Return the legacy parser with additive explicit provider choices."""
    parser = _legacy_cli.build_parser()
    subparsers = next(
        action
        for action in parser._actions
        if getattr(action, "choices", None) and "audit" in action.choices
    )
    audit_parser = subparsers.choices["audit"]
    ai_action = next(action for action in audit_parser._actions if action.dest == "ai_provider")
    legacy_choices = tuple(ai_action.choices or ())
    ai_action.choices = legacy_choices + tuple(
        item for item in _EXTENSION_CHOICES if item not in legacy_choices
    )
    ai_action.help = (
        "semantic analysis provider; AUTO remains the homologated "
        "OpenAI/DeepSeek/MiMo chain, extension providers are explicit-only"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the legacy CLI with only provider factory/parser/M20 routing extended."""
    original_build_parser = _legacy_cli.build_parser
    original_provider_builder = _legacy_cli.build_semantic_provider
    original_m20_router = _m20.build_content_remediation_router
    try:
        _legacy_cli.build_parser = build_parser
        _legacy_cli.build_semantic_provider = build_semantic_provider
        _m20.build_content_remediation_router = build_content_remediation_router
        return _legacy_cli.main(list(argv) if argv is not None else None)
    finally:
        _legacy_cli.build_parser = original_build_parser
        _legacy_cli.build_semantic_provider = original_provider_builder
        _m20.build_content_remediation_router = original_m20_router
