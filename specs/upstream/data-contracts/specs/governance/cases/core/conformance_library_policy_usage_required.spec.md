# Governance Cases

## DCGOV-CONF-POLICY-LIB-001

```yaml contract-spec
id: DCGOV-CONF-POLICY-LIB-001
title: conformance governance checks require library-backed policy calls
purpose: Ensures conformance-prefixed governance checks use shared spec-lang library wiring
  and evaluate library calls.
type: contract.check
harness:
  root: .
  conformance_policy_library_requirements:
    cases_path: /specs/governance/cases
    case_file_pattern: '*.spec.md'
    ignore_checks:
    - conformance.library_policy_usage_required
  check:
    profile: governance.scan
    config:
      check: conformance.library_policy_usage_required
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
      - conformance.library_policy_usage_required
    imports:
    - from: artifact
      names:
      - summary_json
```
