# Governance Cases

## DCGOV-CONF-PORT-001

```yaml contract-spec
id: DCGOV-CONF-PORT-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: conformance cases keep runner logic under harness
purpose: Ensures portable conformance fixtures do not place runner/setup keys at top level.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: conformance.no_runner_logic_outside_harness
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
      - conformance.no_runner_logic_outside_harness
    imports:
    - from: artifact
      names:
      - summary_json
```
