```yaml contract-spec
id: DCGOV-SCHEMA-REG-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: schema registry compiled artifact is synchronized
purpose: Ensures checked-in schema registry compiled artifact matches current registry source
  files.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.registry_compiled_sync
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
      - schema.registry_compiled_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
