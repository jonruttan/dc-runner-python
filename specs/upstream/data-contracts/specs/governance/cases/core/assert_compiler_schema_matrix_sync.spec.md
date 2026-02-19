# Governance Cases

## DCGOV-ASSERT-SYNC-001

```yaml contract-spec
id: DCGOV-ASSERT-SYNC-001
title: compiler behavior stays aligned with universal assertion contract
purpose: Ensures compiler operator handling, schema wording, and assertion contract wording
  stay synchronized for universal evaluate core semantics.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: assert.compiler_schema_matrix_sync
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
      - assert.compiler_schema_matrix_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
