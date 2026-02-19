# Governance Cases

## DCGOV-CONTRACT-002

```yaml contract-spec
id: DCGOV-CONTRACT-002
title: contract must-rule coverage stays complete
purpose: Ensures all MUST policy rules remain covered by traceability evidence and keeps overall
  contract coverage above a minimum baseline.
type: contract.check
harness:
  root: .
  contract_coverage:
    require_all_must_covered: true
    min_coverage_ratio: 0.5
  check:
    profile: governance.scan
    config:
      check: contract.coverage_threshold
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
      - contract.coverage_threshold
    imports:
    - from: artifact
      names:
      - summary_json
```
