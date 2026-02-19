# Governance Cases

## DCGOV-RUNTIME-ENTRY-001

```yaml contract-spec
id: DCGOV-RUNTIME-ENTRY-001
title: gate scripts use a single public runner entrypoint
purpose: Ensures gate scripts reference only the canonical public runner entrypoint.
type: contract.check
harness:
  root: .
  public_runner_entrypoint:
    required_entrypoint: runners/public/runner_adapter.sh
    gate_files:
    - scripts/ci_gate.sh
    - scripts/core_gate.sh
    - scripts/docs_doctor.sh
  forbidden_tokens:
  - dc-runner-rust
  - dc-runner-python
  forbidden_paths:
  - scripts/runner_adapter.sh
  - scripts/rust/runner_adapter.sh
  - scripts/python/runner_adapter.sh
  - scripts/php/conformance_runner.php
  - scripts/php/spec_runner.php
  check:
    profile: governance.scan
    config:
      check: runtime.public_runner_entrypoint_single
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
        - check_id
      - runtime.public_runner_entrypoint_single
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    imports:
    - from: artifact
      names:
      - summary_json
```
