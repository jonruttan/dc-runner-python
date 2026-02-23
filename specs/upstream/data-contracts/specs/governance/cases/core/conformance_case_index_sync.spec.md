```yaml contract-spec
id: DCGOV-CONF-INDEX-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: conformance index stays in sync with fixture ids
purpose: Ensures conformance case index includes all fixture ids and no stale ids.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: conformance.case_index_sync
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
      - conformance.case_index_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
