"""Command-line interface for SearchGEO Readiness Auditor."""

from __future__ import annotations

import argparse
import ipaddress
import logging
import re
import tomllib
from urllib.parse import urlsplit

from searchgeo import __version__
from searchgeo.config import load_config
from searchgeo.logging_config import configure_logging

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

    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser("audit", help="validate and accept an audit target")
    audit_parser.add_argument("target", help="domain or HTTP(S) URL to audit")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config()
        configure_logging(config.log_level)
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        parser.error(str(exc))

    if args.command == "audit":
        try:
            target = validate_target(args.target)
        except ValueError as exc:
            parser.error(str(exc))

        _LOGGER.info("Accepted audit target: %s", target)
        print(f"Target accepted: {target}")
        print("Audit execution is not implemented in M0.")
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2
