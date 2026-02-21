```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: runtime python code does not duplicate governed config literals
purpose: Enforces centralized configuration by rejecting duplicated governed literals in runtime
  python sources.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.config_literals
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
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - runtime.config_literals
    imports:
    - from: artifact
      names:
      - summary_json
```
