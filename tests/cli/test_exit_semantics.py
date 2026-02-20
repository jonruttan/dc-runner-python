import pytest

from spec_runner import spec_lang_commands


def test_main_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc:
        spec_lang_commands.main(["--help"])
    assert int(exc.value.code) == 0


def test_main_unknown_command_exits_two() -> None:
    with pytest.raises(SystemExit) as exc:
        spec_lang_commands.main(["unknown-command"])
    assert int(exc.value.code) == 2
