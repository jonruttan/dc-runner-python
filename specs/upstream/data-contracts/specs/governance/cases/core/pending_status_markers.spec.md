```yaml contract-spec
id: DCGOV-PENDING-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: pending specs remain draft-only and must not include resolved/completed markers
purpose: Ensures pending-spec files do not retain completed markers and keeps completed work
  out of pending.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: pending.no_resolved_markers
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
      - pending.no_resolved_markers
    imports:
    - from: artifact
      names:
      - summary_json
```
