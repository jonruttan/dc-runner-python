# Governance Cases

## DCGOV-SPECLAYOUT-INDEX-001

```yaml contract-spec
id: DCGOV-SPECLAYOUT-INDEX-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: spec domain indexes are synchronized
purpose: Ensures each domain index tracks all spec files in its subtree and has no stale paths.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: spec.domain_index_sync
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
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - spec.domain_index_sync
```
