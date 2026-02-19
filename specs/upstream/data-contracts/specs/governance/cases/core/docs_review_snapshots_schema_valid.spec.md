# Governance Cases

## DCGOV-DOCS-REF-015

```yaml contract-spec
id: DCGOV-DOCS-REF-015
title: active review snapshots validate against canonical contract
purpose: Ensures docs/reviews/snapshots contains canonical machine-consumable snapshots with valid section order and candidate schema.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.review_snapshots_schema_valid
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
      - docs.review_snapshots_schema_valid
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
