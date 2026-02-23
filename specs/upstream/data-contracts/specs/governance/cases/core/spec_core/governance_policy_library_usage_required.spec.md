```yaml contract-spec
id: DCGOV-POLICY-LIB-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: governance policy expressions require shared library wiring
purpose: Ensures governance decision policies use shared spec-lang libraries and call exported
  library symbols.
type: contract.check
harness:
  root: .
  policy_library_requirements:
    cases_path: /specs/governance/cases
    case_file_pattern: '*.spec.md'
    ignore_checks:
    - governance.policy_library_usage_required
  check:
    profile: governance.scan
    config:
      check: governance.policy_library_usage_required
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
      - governance.policy_library_usage_required
    imports:
    - from: artifact
      names:
      - summary_json
```
