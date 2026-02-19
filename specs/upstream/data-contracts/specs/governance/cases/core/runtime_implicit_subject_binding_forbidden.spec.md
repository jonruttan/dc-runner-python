# Governance Cases

## DCGOV-RUNTIME-CONFIG-009

```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-009
title: implicit subject binding is forbidden
purpose: Ensures evaluator does not inject subject implicitly and requires explicit imports.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.implicit_subject_binding_forbidden
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
