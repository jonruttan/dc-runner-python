# Governance Cases

## DCGOV-DOCS-SPECCASE-002

```yaml contract-spec
id: DCGOV-DOCS-SPECCASE-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: spec case catalog artifacts are synchronized
purpose: Ensures generated spec case catalog and markdown references stay in sync.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.spec_case_catalog_sync
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
      - docs.spec_case_catalog_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
