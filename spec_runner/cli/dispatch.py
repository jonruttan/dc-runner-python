from __future__ import annotations

from spec_runner.cli.types import CommandSpec


def dispatch_command(registry: dict[str, CommandSpec], command: str, forwarded: list[str]) -> int:
    spec = registry.get(command)
    if spec is None:
        return 2
    return int(spec.handler(list(forwarded)))
