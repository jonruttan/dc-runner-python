```yaml contract-spec
id: DCGOV-SCHEMA-CONTRACT-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: contract target and on keys are forbidden
purpose: Ensures canonical contract steps use imports bindings instead of target/on keys.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.contract_target_on_forbidden
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
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
```
