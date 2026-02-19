# Governance Cases

## DCGOV-ASSERT-SUBJECT-001

```yaml contract-spec
id: DCGOV-ASSERT-SUBJECT-001
title: type contracts define subject semantics
purpose: Ensures harness and type contracts define target subject semantics and avoid per-type
  operator allowlists.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: assert.type_contract_subject_semantics_sync
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
      - assert.type_contract_subject_semantics_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
