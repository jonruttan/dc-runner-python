```yaml contract-spec
id: DCGOV-POLICY-REQ-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: governance checks require structured assertion targets
purpose: Ensures governance cases validate deterministic structured result targets instead
  of relying on PASS text markers as primary contract truth.
type: contract.check
harness:
  root: .
  structured_assertions:
    cases_path: /specs/governance/cases
    case_file_pattern: '*.spec.md'
    ignore_checks:
    - governance.structured_assertions_required
  check:
    profile: governance.scan
    config:
      check: governance.structured_assertions_required
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
      - governance.structured_assertions_required
    imports:
    - from: artifact
      names:
      - summary_json
```
