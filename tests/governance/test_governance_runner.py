from spec_runner.governance.runner import governance_check_id, is_governance_case_payload
from spec_runner.governance.runner import run_governance_check


def test_is_governance_case_payload_and_check_id() -> None:
    case = {
        "type": "contract.check",
        "harness": {"check": {"profile": "governance.scan", "config": {"check": "docs.stdlib_examples_complete"}}},
    }
    assert is_governance_case_payload(case)
    assert governance_check_id(case) == "docs.stdlib_examples_complete"


def test_non_governance_payload_rejected() -> None:
    case = {"type": "contract.check", "harness": {"check": {"profile": "cli.run"}}}
    assert not is_governance_case_payload(case)


def test_run_governance_check_forwards_to_legacy(monkeypatch) -> None:
    import spec_runner.governance_runtime as legacy

    called: dict[str, object] = {}

    def _fake_run(case, *, ctx) -> None:
        called["case"] = case
        called["ctx"] = ctx

    monkeypatch.setattr(legacy, "run_governance_check", _fake_run)
    case_obj = object()
    ctx_obj = object()
    run_governance_check(case_obj, ctx=ctx_obj)
    assert called == {"case": case_obj, "ctx": ctx_obj}
