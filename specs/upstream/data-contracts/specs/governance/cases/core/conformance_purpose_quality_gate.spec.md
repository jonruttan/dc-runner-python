```yaml contract-spec
id: DCGOV-CONF-PURPOSE-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: conformance purpose quality remains warning free
purpose: Ensures conformance purpose lint policy and case purpose text stay clean with no
  accumulated warning debt.
type: contract.check
harness:
  root: .
  purpose_quality:
    cases: specs/conformance/cases
    max_total_warnings: 0
    fail_on_policy_errors: true
    fail_on_severity: warn
  check:
    profile: governance.scan
    config:
      check: conformance.purpose_quality_gate
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
      - conformance.purpose_quality_gate
    imports:
    - from: artifact
      names:
      - summary_json
```
