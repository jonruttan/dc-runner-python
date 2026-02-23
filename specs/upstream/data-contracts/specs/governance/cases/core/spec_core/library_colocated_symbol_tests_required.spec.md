```yaml contract-spec
id: DCGOV-LIB-SINGLE-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: library exports are referenced by executable tests
purpose: Ensures library exported symbols are exercised by colocated or downstream executable
  assertion/policy usage.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: library.colocated_symbol_tests_required
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
