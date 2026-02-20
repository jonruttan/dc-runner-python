from __future__ import annotations

import argparse


ALIASES = {
    "evaluate-style": "spec-lang-format",
}


def normalize_argv(argv: list[str]) -> list[str]:
    normalized = list(argv)
    if normalized:
        normalized[0] = ALIASES.get(normalized[0], normalized[0])
    return normalized


def parse_command_args(argv: list[str], *, command_names: tuple[str, ...]) -> tuple[str, list[str]]:
    ap = argparse.ArgumentParser(description="Spec-lang backed command entrypoints.")
    ap.add_argument("command", choices=command_names, help="Command to run.")
    ap.add_argument("args", nargs=argparse.REMAINDER)
    ns = ap.parse_args(normalize_argv(argv))
    return str(ns.command), list(ns.args or [])
