"""Public interactive-console entrypoint.

Keeps the established console runtime while replacing the legacy flat environment
editor with the grouped, guided environment configuration surface.
"""
from __future__ import annotations

from searchgeo import interactive_console
from searchgeo.console_environment import environment_menu


def main() -> int:
    interactive_console._environment_menu = environment_menu
    return interactive_console.main()


if __name__ == "__main__":
    raise SystemExit(main())
