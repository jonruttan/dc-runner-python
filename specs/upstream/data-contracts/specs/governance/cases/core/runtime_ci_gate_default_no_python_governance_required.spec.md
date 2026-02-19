# Governance Cases

## DCGOV-RUNTIME-TRIAGE-015

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-015
title: ci gate default broad governance path is rust-native
purpose: Ensures ci-gate-summary defaults to governance-broad-native and does not route broad
  through Python governance scripts.
type: contract.check
harness:
  root: .
  ci_gate_default_no_python_governance:
    files:
    - /dc-runner-python
    required_tokens:
    - governance-broad-native
    - governance_broad
    forbidden_tokens: []
  check:
    profile: governance.scan
    config:
      check: runtime.ci_gate_default_no_python_governance_required
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
