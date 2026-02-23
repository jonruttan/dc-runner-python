```yaml contract-spec
id: DCGOV-CHAIN-FROM-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: executable cases forbid spec_lang includes
purpose: Ensures executable case types do not use harness.spec_lang.includes and load symbols
  through harness.chain.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.executable_spec_lang_includes_forbidden
  use:
  - ref: /specs/05_libraries/policy/policy_core.spec.md
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
