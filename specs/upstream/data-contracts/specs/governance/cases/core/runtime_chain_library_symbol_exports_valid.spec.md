# runtime.chain_library_symbol_exports_valid

```yaml contract-spec
id: DCGOV-CHAIN-FROM-003
title: chain assert function imports are valid
purpose: Ensures from=assert.function step imports include valid symbol path and contract
  shape.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_library_symbol_exports_valid
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
        - passed
      - true
```
