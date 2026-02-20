import pytest

from spec_runner.cli.registry import build_command_registry, command_names
from spec_runner.cli.types import CommandSpec


def _ok(_: list[str]) -> int:
    return 0


def test_build_command_registry_orders_and_names() -> None:
    registry = build_command_registry((CommandSpec("a", _ok), CommandSpec("b", _ok)))
    assert command_names(registry) == ("a", "b")


def test_build_command_registry_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="duplicate command name"):
        build_command_registry((CommandSpec("a", _ok), CommandSpec("a", _ok)))


def test_build_command_registry_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="command name must be non-empty"):
        build_command_registry((CommandSpec("", _ok),))
