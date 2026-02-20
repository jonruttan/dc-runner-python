# Governance Cases

## DCGOV-SCHEMA-REG-005

```yaml contract-spec
id: DCGOV-SCHEMA-REG-005
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: required schema type profiles exist
purpose: Ensures required type profiles are defined in registry for core runtime case types.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.type_profiles_complete
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
      - schema.type_profiles_complete
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
