```yaml contract-spec
id: DCGOV-DOCS-REF-014
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: review tooling stays synced with canonical candidate schema
purpose: Ensures snapshot scaffolder and pending conversion tooling both use canonical review snapshot schema fields.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.review_tooling_contract_sync
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
      - docs.review_tooling_contract_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
