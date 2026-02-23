```yaml contract-spec
id: DCGOV-DOCS-REF-027
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: discovery review workflow is documented and synced
purpose: Ensures docs/history/reviews README documents scaffold, validate, and pending-conversion flow for the discovery prompt.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.reviews_discovery_workflow_sync
  use:
  - ref: /specs/05_libraries/policy/policy_core.spec.md
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
      - docs.reviews_discovery_workflow_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
