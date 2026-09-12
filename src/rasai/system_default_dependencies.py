"""Dependency normalization for versioned system defaults.

System defaults are a lower-precedence layer. When an explicit higher-precedence override
turns off a parent capability, dependent defaults must not turn that into a configuration
error unless the dependent capability was also explicitly forced on by the operator.
"""
from __future__ import annotations

import os
from types import ModuleType
from typing import Any, Iterable

from rasai.m23_cli import APDEX_ENABLED_ENV
from rasai.m25_cli import UX_ENABLED_ENV

_FALSE_VALUES = frozenset({"0", "false", "no", "off"})
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def normalize_apdex_environment_dependencies(
    state: Any,
    names: Iterable[str] | None,
) -> None:
    """Let an explicit Navigation OFF suppress the lower-precedence Experience default.

    An explicit contradictory ``RASAI_APDEX_EXPERIENCE=true`` is intentionally preserved
    so the existing validator can report the invalid combination instead of silently
    changing an operator choice.
    """
    selected = set(names or ())
    if APDEX_ENABLED_ENV not in selected:
        return

    navigation = (os.environ.get(APDEX_ENABLED_ENV) or "").strip().casefold()
    if navigation not in _FALSE_VALUES:
        return

    experience_explicit = UX_ENABLED_ENV in selected
    experience = (os.environ.get(UX_ENABLED_ENV) or "").strip().casefold()
    if experience_explicit and experience in _TRUE_VALUES:
        return

    if hasattr(state, "apdex_experience"):
        state.apdex_experience = False


def install(console_module: ModuleType) -> None:
    """Wrap the console's M23 environment application at its final integration point."""
    if getattr(console_module, "_rasai_system_default_dependencies_installed", False):
        return

    original = console_module.apply_m23_environment_defaults

    def apply_m23_environment_defaults(state: Any, names: set[str] | None = None):
        normalize_apdex_environment_dependencies(state, names)
        return original(state, names=names)

    console_module.apply_m23_environment_defaults = apply_m23_environment_defaults
    console_module._rasai_system_default_dependencies_installed = True
