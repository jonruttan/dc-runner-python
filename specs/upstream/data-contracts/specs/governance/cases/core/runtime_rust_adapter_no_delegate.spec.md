# Governance Cases

## DCGOV-RUNTIME-CONFIG-006

```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-006
title: rust adapter does not delegate to python shell adapter
purpose: Ensures dc-runner-rust invokes the Rust CLI directly and does not
  call runners/public/runner_adapter.sh.
type: contract.check
harness:
  root: .
  rust_adapter:
    path: /dc-runner-rust
    required_tokens:
    - spec_runner_cli
    - cargo run --quiet
    forbidden_tokens:
    - runners/public/runner_adapter.sh
  check:
    profile: governance.scan
    config:
      check: runtime.rust_adapter_no_delegate
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
      - runtime.rust_adapter_no_delegate
    imports:
    - from: artifact
      names:
      - summary_json
```
