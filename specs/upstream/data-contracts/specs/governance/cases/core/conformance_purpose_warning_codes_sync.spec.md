```yaml contract-spec
id: DCGOV-CONF-PURPOSE-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: purpose warning code doc stays in sync with implementation codes
purpose: Ensures docs for purpose warning codes include all implementation codes and no stale
  entries.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: conformance.purpose_warning_codes_sync
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
      - conformance.purpose_warning_codes_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
