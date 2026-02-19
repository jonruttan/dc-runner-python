# Governance Cases

## DCGOV-RUNTIME-ORCH-001

```yaml contract-spec
id: DCGOV-RUNTIME-ORCH-001
title: gate orchestration verdict is policy-driven via spec-lang
purpose: Ensures CI gate summary determines final verdict from assert-derived step statuses
  without evaluate expressions.
type: contract.check
harness:
  root: .
  orchestration_policy:
    files:
    - path: /dc-runner-python
      required_tokens:
      - _evaluate_gate_policy(
      - all(str(row.get("status", "")) == "pass"
      - policy_verdict
    - path: /specs/governance/cases/core/runtime_orchestration_policy_via_spec_lang.spec.md
      required_tokens:
      - runtime.orchestration_policy_via_spec_lang
      - _evaluate_gate_policy(
    forbidden_tokens: []
  check:
    profile: governance.scan
    config:
      check: runtime.orchestration_policy_via_spec_lang
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
      - runtime.orchestration_policy_via_spec_lang
    imports:
    - from: artifact
      names:
      - summary_json
```
