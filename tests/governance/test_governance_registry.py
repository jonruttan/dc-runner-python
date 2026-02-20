from spec_runner.governance.registry import all_checks, check_ids, checks_by_domain, checks_for_prefix, get_check


def test_registry_contains_required_checks() -> None:
    ids = check_ids()
    assert "docs.stdlib_symbol_docs_complete" in ids
    assert "runtime.contract_job_dispatch_in_contract_required" in ids


def test_registry_grouped_by_domain() -> None:
    grouped = checks_by_domain()
    assert "docs" in grouped
    assert "runtime" in grouped


def test_all_checks_not_empty() -> None:
    checks = all_checks()
    assert checks


def test_get_check_and_prefix_filter() -> None:
    check = get_check(" docs.stdlib_examples_complete ")
    assert callable(check)
    assert checks_for_prefix(())
    docs_only = checks_for_prefix(("docs.",))
    assert docs_only
    assert all(k.startswith("docs.") for k in docs_only)
