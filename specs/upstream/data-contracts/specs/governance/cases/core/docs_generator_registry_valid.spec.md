# Governance Cases

## DCGOV-DOCS-GEN-001

```yaml contract-spec
id: DCGOV-DOCS-GEN-001
title: docs generator registry is valid and complete
purpose: Ensures docs generator registry exists, validates, and includes required surfaces.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.generator_registry_valid
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
      - docs.generator_registry_valid
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
