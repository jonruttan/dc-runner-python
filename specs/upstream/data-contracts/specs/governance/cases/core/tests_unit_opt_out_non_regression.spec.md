```yaml contract-spec
id: DCGOV-TEST-UNIT-OPT-OUT-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: unit test opt-out usage is measured and non-regressing
purpose: Tracks unit-test opt-out usage and enforces a non-regression baseline so opt-out
  coverage is reduced over time.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: tests.unit_opt_out_non_regression
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
        - check_id
      - tests.unit_opt_out_non_regression
```
