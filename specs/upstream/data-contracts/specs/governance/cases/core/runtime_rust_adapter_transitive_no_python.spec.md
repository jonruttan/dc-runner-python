# Governance Cases

## DCGOV-RUNTIME-PYDEP-004

```yaml contract-spec
id: DCGOV-RUNTIME-PYDEP-004
title: rust adapter boundary avoids transitive python delegation tokens
purpose: Ensures rust adapter boundary files do not delegate to python adapter entrypoints
  or direct python execution tokens.
type: contract.check
harness:
  root: .
  rust_transitive_no_python:
    files:
    - dc-runner-rust
    - dc-runner-rust
    forbidden_tokens:
    - runners/public/runner_adapter.sh
    - spec_runner.spec_lang_commands
    - PYTHONPATH
    - python
    - scripts/run_governance_specs.py
  check:
    profile: governance.scan
    config:
      check: runtime.rust_adapter_transitive_no_python
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
      - runtime.rust_adapter_transitive_no_python
    imports:
    - from: artifact
      names:
      - summary_json
```
