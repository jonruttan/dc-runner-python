# Governance Cases

## DCGOV-RUNTIME-FAILFAST-002

```yaml contract-spec
id: DCGOV-RUNTIME-FAILFAST-002
title: gate summary payload includes skipped step contract
purpose: Ensures gate summary output includes skipped-step and abort metadata fields.
type: contract.check
harness:
  root: .
  gate_skipped_contract:
    files:
    - /dc-runner-python
    - /dc-runner-rust
    required_tokens:
    - skipped_step_count
    - first_failure_step
    - aborted_after_step
    - blocked_by
    - skip_reason
  check:
    profile: governance.scan
    config:
      check: runtime.gate_skipped_steps_contract_required
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
```
