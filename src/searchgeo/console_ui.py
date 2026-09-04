"""Terminal presentation helpers for the optional interactive console."""
from __future__ import annotations

import os
import sys

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"


def supports_color() -> bool:
    """Return whether ANSI presentation should be emitted."""
    if os.environ.get("NO_COLOR") is not None:
        return False
    if not sys.stdout.isatty():
        return False
    return os.environ.get("TERM", "").casefold() != "dumb"


def paint(text: object, color: str, *, bold: bool = False) -> str:
    raw = str(text)
    if not supports_color():
        return raw
    prefix = (BOLD if bold else "") + color
    return f"{prefix}{raw}{RESET}"


def clear_screen() -> None:
    """Redraw the interactive console as one logical screen instead of stacking menus."""
    if not sys.stdout.isatty():
        return
    # ANSI clear + cursor home works in modern Windows Terminal/PowerShell and Unix terminals.
    # A textual fallback is intentionally avoided because it would stack output instead of redrawing.
    print("\033[2J\033[H", end="", flush=True)


def status_color(status: str) -> str:
    normalized = status.strip().upper()
    if normalized in {"COMPLETE", "READY", "SUCCESS", "OK"} or normalized.startswith("COMPLETE"):
        return GREEN
    if any(token in normalized for token in ("FAIL", "ERROR", "BLOCK", "CRITICAL", "QUARANTIN")):
        return RED
    if any(token in normalized for token in ("START", "DISCOVER", "ACQUIR", "ANALYZ", "SCOR", "REPORT", "WEB_PERFORMANCE", "FINALIZ")):
        return YELLOW
    return CYAN


def bool_badge(enabled: bool) -> str:
    return paint("ON" if enabled else "OFF", GREEN if enabled else DIM)


def availability_badge(available: bool) -> str:
    return paint("APTO" if available else "INDISPONÍVEL", GREEN if available else RED, bold=True)


def cost_color(level: str) -> str:
    normalized = level.strip().upper()
    return {
        "NENHUM": GREEN,
        "BAIXO": CYAN,
        "MÉDIO": YELLOW,
        "MEDIO": YELLOW,
        "ALTO": MAGENTA,
        "EXCESSIVO": RED,
    }.get(normalized, WHITE)
