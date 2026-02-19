# Governance Cases

## DCGOV-SCHEMA-REG-001

```yaml contract-spec
id: DCGOV-SCHEMA-REG-001
title: schema registry model is present and valid
purpose: Ensures schema registry source files and contract docs are present and compile without
  registry errors.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.registry_valid
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
      - schema.registry_valid
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
