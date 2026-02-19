# Governance Cases

## DCGOV-POLICY-LIB-001

```yaml contract-spec
id: DCGOV-POLICY-LIB-001
title: governance library-backed policy usage is non-regressing
purpose: Enforces monotonic non-regression for governance policy expressions that use shared
  spec-lang libraries.
type: contract.check
harness:
  root: .
  policy_library_usage_non_regression:
    baseline_path: /specs/governance/metrics/spec_lang_adoption_baseline.json
    summary_fields:
      governance_library_backed_policy_ratio: non_decrease
    segment_fields:
      governance:
        library_backed_policy_ratio: non_decrease
    epsilon: 1.0e-12
    spec_lang_adoption:
      roots:
      - /specs/conformance/cases
      - /specs/governance/cases
      - /specs/impl
      segment_rules:
      - prefix: specs/conformance/cases
        segment: conformance
      - prefix: specs/governance/cases
        segment: governance
      - prefix: specs/impl
        segment: impl
      recursive: true
  check:
    profile: governance.scan
    config:
      check: governance.policy_library_usage_non_regression
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
      - governance.policy_library_usage_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
