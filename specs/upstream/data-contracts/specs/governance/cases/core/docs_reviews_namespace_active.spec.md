# Governance Cases

## DCGOV-DOCS-LAYOUT-004

```yaml contract-spec
id: DCGOV-DOCS-LAYOUT-004
title: active review assets live under docs/history/reviews
purpose: Enforces docs/history/reviews as canonical active review namespace while keeping historical review archives out of active workflow references.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.reviews_namespace_active
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
    - summary_json
  steps:
  - id: assert_1
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.reviews_namespace_active
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
