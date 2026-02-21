```yaml contract-spec
id: DCGOV-SCHEMA-REG-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: schema registry docs snapshot is synchronized
purpose: Ensures schema_v1 markdown contains synchronized generated registry snapshot markers
  and tokens.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.registry_docs_sync
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
      - schema.registry_docs_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
