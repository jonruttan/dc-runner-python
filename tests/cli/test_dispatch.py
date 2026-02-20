import pytest

from spec_runner.cli.dispatch import dispatch_command
from spec_runner.cli.parser import parse_command_args
from spec_runner.cli.registry import build_command_registry, command_names
from spec_runner.cli.types import CommandSpec


def _capture(args: list[str]) -> int:
    _capture.last = list(args)
    return 7


def test_parse_and_dispatch_with_remainder_args() -> None:
    registry = build_command_registry((CommandSpec("spec-lang-format", _capture),))
    command, forwarded = parse_command_args(
        ["spec-lang-format", "--check", "specs"], command_names=command_names(registry)
    )
    rc = dispatch_command(registry, command, forwarded)
    assert rc == 7
    assert _capture.last == ["--check", "specs"]


def test_alias_evaluate_style_maps_to_spec_lang_format() -> None:
    registry = build_command_registry((CommandSpec("spec-lang-format", _capture),))
    command, forwarded = parse_command_args(["evaluate-style", "--help"], command_names=command_names(registry))
    assert command == "spec-lang-format"
    assert forwarded == ["--help"]


def test_parse_unknown_command_exits_usage() -> None:
    registry = build_command_registry((CommandSpec("spec-lang-format", _capture),))
    with pytest.raises(SystemExit) as exc:
        parse_command_args(["unknown-cmd"], command_names=command_names(registry))
    assert int(exc.value.code) == 2


def test_dispatch_unknown_command_returns_two() -> None:
    registry = build_command_registry((CommandSpec("spec-lang-format", _capture),))
    rc = dispatch_command(registry, "missing-command", [])
    assert rc == 2
