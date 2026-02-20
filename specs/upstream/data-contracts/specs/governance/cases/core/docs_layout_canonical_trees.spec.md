# Governance Cases

## DCGOV-DOCS-LAYOUT-001

```yaml contract-spec
id: DCGOV-DOCS-LAYOUT-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: docs layout canonical trees exist
purpose: Enforces canonical docs root namespaces.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.layout_canonical_trees
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
      - docs.layout_canonical_trees
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
