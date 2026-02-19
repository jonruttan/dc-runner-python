# Governance Cases

## DCGOV-RUST-PRIMARY-006

```yaml contract-spec
id: DCGOV-RUST-PRIMARY-006
title: rust-primary adapter executes success-path smoke command deterministically
purpose: Ensures the Rust adapter can execute a supported success-path command with deterministic
  success output and exit-code behavior.
type: contract.check
harness:
  root: .
  rust_adapter_exec_smoke:
    command:
    - dc-runner-rust
    - style-check
    expected_exit_codes:
    - 0
    required_output_tokens:
    - 'OK: evaluate style formatting is canonical'
    forbidden_output_tokens:
    - unsupported runner adapter subcommand
    - rust runner adapter subcommand not yet implemented
    timeout_seconds: 180
  check:
    profile: governance.scan
    config:
      check: runtime.rust_adapter_exec_smoke
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
      - runtime.rust_adapter_exec_smoke
    imports:
    - from: artifact
      names:
      - summary_json
```
