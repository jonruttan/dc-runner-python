```yaml contract-spec
id: DCGOV-OPS-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: orchestration ops capability bindings are enforced
purpose: Ensures orchestration tools and case capability bindings remain synchronized.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: orchestration.ops_capability_bindings
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
      - orchestration.ops_capability_bindings
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
