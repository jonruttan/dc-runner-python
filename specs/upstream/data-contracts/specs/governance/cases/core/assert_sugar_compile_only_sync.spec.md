# Governance Cases

## DCGOV-ASSERT-COMPILE-001

```yaml contract-spec
id: DCGOV-ASSERT-COMPILE-001
title: compiler keeps sugar operators compile-only
purpose: Ensures compiler and runtime assertion path keep non-evaluate operators as compile-only
  sugar with spec-lang execution.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: assert.sugar_compile_only_sync
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
      - assert.sugar_compile_only_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
