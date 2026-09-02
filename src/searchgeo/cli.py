"""Command-line interface for SearchGEO Readiness Auditor."""

from __future__ import annotations

import argparse
import ipaddress
import logging
import os
from pathlib import Path
import re
import tomllib
from urllib.parse import urlsplit

from searchgeo import __version__
from searchgeo.audit_runner import run_audit
from searchgeo.config import load_config
from searchgeo.logging_config import configure_logging
from searchgeo.semantic import NoneProvider, OpenAIProvider

_LOGGER = logging.getLogger(__name__)
_DOMAIN_LABEL = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")


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
    audit_parser.add_argument("--ai-provider", choices=("none", "openai"), default="none", help="optional semantic analysis provider")
    audit_parser.add_argument("--ai-model", help="OpenAI model when --ai-provider=openai; can also use SEARCHGEO_OPENAI_MODEL")

    return parser


def _semantic_provider(args: argparse.Namespace):
    if args.ai_provider == "none":
        return NoneProvider()
    model = (args.ai_model or os.environ.get("SEARCHGEO_OPENAI_MODEL") or "").strip()
    if not model:
        raise ValueError("--ai-model or SEARCHGEO_OPENAI_MODEL is required when --ai-provider=openai")
    return OpenAIProvider(model=model)


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
            audit_target: str | tuple[str, ...] = targets[0] if len(targets) == 1 else targets
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
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2
