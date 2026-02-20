from pathlib import Path

from spec_runner.governance.types import infer_check_domain, normalize_root


def test_infer_check_domain_prefixed_and_misc() -> None:
    assert infer_check_domain("docs.stdlib_examples_complete") == "docs"
    assert infer_check_domain("no_dot_check") == "misc"


def test_normalize_root_none_and_value() -> None:
    assert normalize_root(None) == Path(".").resolve()
    assert normalize_root("spec_runner") == (Path("spec_runner")).resolve()
