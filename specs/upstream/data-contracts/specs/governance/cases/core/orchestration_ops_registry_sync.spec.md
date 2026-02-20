# Governance Cases

## DCGOV-OPS-003

```yaml contract-spec
id: DCGOV-OPS-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: orchestration ops registries are synchronized and complete
purpose: Ensures runner tool registries include required fields and declared tool ids.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: orchestration.ops_registry_sync
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
      - orchestration.ops_registry_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
