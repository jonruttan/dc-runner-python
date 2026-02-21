```yaml contract-spec
id: DCGOV-NORM-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: normalization profile defines required source-of-truth fields
purpose: Ensures normalization profile exists and includes all required top-level keys and
  path scopes.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: normalization.profile_sync
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
      - normalization.profile_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
