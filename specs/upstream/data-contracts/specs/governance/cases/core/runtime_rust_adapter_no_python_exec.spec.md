# Governance Cases

## DCGOV-RUST-PRIMARY-008

```yaml contract-spec
id: DCGOV-RUST-PRIMARY-008
title: rust runner interface avoids direct python execution tokens
purpose: Ensures the Rust runner interface implementation does not hardcode direct python
  executable invocation.
type: contract.check
harness:
  root: .
  rust_no_python_exec:
    path: /dc-runner-rust
    forbidden_tokens:
    - spec_runner.spec_lang_commands
    - PYTHONPATH
    - python
    - python3
    - PYTHON_BIN
    - resolve_python_bin
    - scripts/run_governance_specs.py
  check:
    profile: governance.scan
    config:
      check: runtime.rust_adapter_no_python_exec
  use:
  - ref: /specs/libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - runtime.rust_adapter_no_python_exec
    imports:
    - from: artifact
      names:
      - summary_json
```
