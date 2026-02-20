from spec_runner.governance import checks_contract, checks_docs, checks_library, checks_runtime, checks_schema


def test_domain_check_modules_expose_prefixed_checks() -> None:
    assert any(k.startswith("docs.") for k in checks_docs.checks())
    assert any(k.startswith("runtime.") for k in checks_runtime.checks())
    assert any(k.startswith("schema.") for k in checks_schema.checks())
    assert any(k.startswith("contract.") or k.startswith("conformance.") for k in checks_contract.checks())
    assert any(k.startswith("library.") or k.startswith("normalization.") for k in checks_library.checks())
