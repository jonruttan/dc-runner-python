from spec_runner.cli.dispatch import dispatch_command
from spec_runner.cli.parser import parse_command_args
from spec_runner.cli.registry import build_command_registry, command_names
from spec_runner.cli.types import CommandSpec

__all__ = [
    "CommandSpec",
    "build_command_registry",
    "command_names",
    "parse_command_args",
    "dispatch_command",
]
