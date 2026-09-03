"""Command-line interface for SearchGEO Readiness Auditor."""

from __future__ import annotations

import argparse
import ipaddress
import logging
import math
import os
from pathlib import Path
import re
import tomllib
from urllib.parse import urlsplit

from searchgeo import __version__
from searchgeo.audit_runner import run_audit
from searchgeo.config import load_config
from searchgeo.logging_config import configure_logging
from searchgeo.m18_ai import build_semantic_provider

_LOGGER = logging.getLogger(__name__)
_DOMAIN_LABEL = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
_DEFAULT_AI_TIMEOUT_SECONDS = 180.0
_AI_TIMEOUT_ENV = "SEARCHGEO_AI_TIMEOUT_SECONDS"


def _valid_hostname(hostname: str) -> bool:
    if hostname.lower() == "localhost":
        return True

    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        return True

    try:
        ascii_hostname = hostname.rstrip(".").encode("idna").decode("ascii")
    except UnicodeError:
        return False

    if len(ascii_hostname) > 253 or "." not in ascii_hostname:
        return False

    return all(_DOMAIN_LABEL.fullmatch(label) for label in ascii_hostname.split("."))


def validate_target(value: str) -> str:
    """Validate a domain or an HTTP(S) URL without performing network access."""

    target = value.strip()
    if not target or any(character.isspace() for character in target):
        raise ValueError("target must be a non-empty domain or HTTP(S) URL")

    has_scheme = "://" in target
    candidate = target if has_scheme else f"https://{target}"
    parsed = urlsplit(candidate)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("target URL scheme must be http or https")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("target must not contain user credentials")
    if parsed.hostname is None or not _valid_hostname(parsed.hostname):
        raise ValueError("target must contain a valid hostname, IP address, or localhost")

    try:
        parsed.port
    except ValueError as exc:
        raise ValueError("target contains an invalid port") from exc

    if not has_scheme and (parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        raise ValueError("a target with path, query, or fragment must include http:// or https://")

    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="searchgeo")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", help="path to searchgeo.toml; currently used for application logging settings")

    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser("audit", help="execute a local SearchGEO readiness audit")
    audit_parser.add_argument(
        "target",
        nargs="*",
        help="one or more domains/HTTP(S) URLs to audit in the same audit_id",
    )
    audit_parser.add_argument(
        "--urls-file",
        help="UTF-8 text file with one domain/HTTP(S) URL per line; blank lines and # comments are ignored",
    )
    audit_parser.add_argument("--project", help="human-readable project name")
    audit_parser.add_argument("--language", default="pt-BR", help="primary content/reporting language context")
    audit_parser.add_argument("--market", default="BR", help="market context")
    audit_parser.add_argument("--max-pages", type=int, default=100, help="deterministic maximum number of audited pages")
    audit_parser.add_argument("--audits-root", default="audits", help="local directory that will contain audit workspaces")
    audit_parser.add_argument(
        "--ai-provider",
        choices=("none", "openai", "deepseek", "mimo", "auto"),
        default="none",
        help="semantic analysis provider or deterministic AUTO routing",
    )
    audit_parser.add_argument(
        "--ai-model",
        help="model override for an explicit provider; AUTO uses SEARCHGEO_<PROVIDER>_MODEL",
    )

    return parser


def _configured_ai_timeout_seconds() -> float:
    raw = os.environ.get(_AI_TIMEOUT_ENV)
    if raw is None or not raw.strip():
        return _DEFAULT_AI_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{_AI_TIMEOUT_ENV} must be a positive number of seconds") from exc
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{_AI_TIMEOUT_ENV} must be a positive finite number of seconds")
    return value


def _apply_ai_timeout(provider, timeout: float):
    routed = getattr(provider, "providers", None)
    if isinstance(routed, tuple):
        for item in routed:
            if hasattr(item, "timeout"):
                item.timeout = timeout
    elif hasattr(provider, "timeout"):
        provider.timeout = timeout
    return provider


def _semantic_provider(args: argparse.Namespace):
    if args.ai_provider == "auto" and args.ai_model:
        raise ValueError("--ai-model cannot be used with --ai-provider=auto; configure per-provider SEARCHGEO_*_MODEL variables")
    provider = build_semantic_provider(args.ai_provider, model_override=args.ai_model)
    if args.ai_provider == "none":
        return provider
    return _apply_ai_timeout(provider, _configured_ai_timeout_seconds())


def _audit_targets(args: argparse.Namespace) -> tuple[str, ...]:
    values = list(args.target)
    if args.urls_file:
        path = Path(args.urls_file)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise ValueError(f"cannot read --urls-file {path}: {exc}") from exc
        values.extend(
            line.strip()
            for line in lines
            if line.strip() and not line.lstrip().startswith("#")
        )
    if not values:
        raise ValueError("provide at least one target URL/domain or --urls-file")
    return tuple(validate_target(value) for value in values)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        configure_logging(config.log_level)
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        parser.error(str(exc))

    if args.command == "audit":
        try:
            targets = _audit_targets(args)
            if args.max_pages <= 0:
                raise ValueError("--max-pages must be greater than zero")
            provider = _semantic_provider(args)
            # A urls file is an explicit URL_SET by definition, even when it
            # contains one URL after comments/blank lines are removed. Direct
            # CLI input remains backward compatible: one positional target is
            # the classic single-target mode; multiple positionals are URL_SET.
            audit_target: str | tuple[str, ...] = (
                targets
                if args.urls_file or len(targets) > 1
                else targets[0]
            )
            result = run_audit(
                audit_target,
                audits_root=Path(args.audits_root),
                project_name=args.project,
                language=args.language,
                market=args.market,
                max_pages=args.max_pages,
                semantic_provider=provider,
            )
        except (OSError, ValueError, RuntimeError) as exc:
            _LOGGER.exception("Audit failed")
            parser.error(str(exc))

        print(f"Auditoria concluída: {result.audit_id}")
        print(f"Status: {result.completion_status.value}")
        print(f"Páginas auditadas: {result.audited_pages}")
        print(f"Problemas identificados: {result.finding_count}")
        print(f"Recomendações: {result.recommendation_count}")
        print(f"Relatório: {result.report_path}")
        remediation_path = result.audit_root / "remediation.html"
        if remediation_path.is_file():
            print(f"Relatório por problemas: {remediation_path}")
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2
