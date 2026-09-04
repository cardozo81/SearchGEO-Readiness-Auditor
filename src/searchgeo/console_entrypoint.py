"""Public entrypoint for the interactive SearchGEO console.

The established console remains the runtime implementation. This entrypoint
installs the grouped environment editor before delegating to it, avoiding a
second audit/configuration engine.
"""
from __future__ import annotations

from searchgeo import interactive_console
from searchgeo.console_environment import environment_menu


def main() -> int:
    interactive_console._environment_menu = environment_menu
    return interactive_console.main()


if __name__ == "__main__":
    raise SystemExit(main())
