# Governance Cases

## DCGOV-REF-SYMBOLS-002

```yaml contract-spec
id: DCGOV-REF-SYMBOLS-002
title: governance policy symbols resolve through declared libraries
purpose: Ensures every dotted var reference used in evaluate resolves from declared library
  symbols.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: reference.policy_symbols_resolve
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
      - reference.policy_symbols_resolve
```
