# Governance Cases

## DCGOV-REF-SYMBOLS-001

```yaml contract-spec
id: DCGOV-REF-SYMBOLS-001
title: referenced library symbols resolve
purpose: Ensures harness.spec_lang exports and library symbols resolve deterministically.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: reference.symbols_exist
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
      - reference.symbols_exist
```
