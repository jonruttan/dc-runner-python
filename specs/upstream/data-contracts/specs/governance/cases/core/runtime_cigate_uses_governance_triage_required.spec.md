# Governance Cases

## DCGOV-RUNTIME-TRIAGE-003

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-003
title: ci gate summary uses governance triage and emits triage metadata
purpose: Ensures both Python and Rust ci-gate-summary paths reference governance triage flow.
type: contract.check
harness:
  root: .
  cigate_governance_triage:
    files:
    - /dc-runner-python
    - /dc-runner-rust
    required_tokens:
    - governance_broad
    - triage_attempted
    - triage_mode
    - triage_result
    - failing_check_ids
    - failing_check_prefixes
    - stall_detected
    - stall_phase
  check:
    profile: governance.scan
    config:
      check: runtime.cigate_uses_governance_triage_required
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
