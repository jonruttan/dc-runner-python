from __future__ import annotations

from collections.abc import Iterable

from spec_runner.cli.types import CommandSpec


def build_command_registry(specs: Iterable[CommandSpec]) -> dict[str, CommandSpec]:
    registry: dict[str, CommandSpec] = {}
    for spec in specs:
        name = str(spec.name).strip()
        if not name:
            raise ValueError("command name must be non-empty")
        if name in registry:
            raise ValueError(f"duplicate command name: {name}")
        registry[name] = spec
    return registry


def command_names(registry: dict[str, CommandSpec]) -> tuple[str, ...]:
    return tuple(registry.keys())
