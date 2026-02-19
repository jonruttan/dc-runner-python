# Governance Cases

## DCGOV-IMPL-SPECLANG-003

```yaml contract-spec
id: DCGOV-IMPL-SPECLANG-003
title: impl library-backed assertion usage is non-regressing
purpose: Enforces monotonic non-regression for impl case wiring to shared spec-lang helper
  libraries.
type: contract.check
harness:
  root: .
  impl_library_usage_non_regression:
    baseline_path: /specs/governance/metrics/spec_lang_adoption_baseline.json
    summary_fields:
      impl_library_backed_case_ratio: non_decrease
    segment_fields:
      impl:
        library_backed_case_ratio: non_decrease
    epsilon: 1.0e-12
    spec_lang_adoption:
      roots:
      - /specs/impl
      segment_rules:
      - prefix: specs/impl
        segment: impl
      recursive: true
  check:
    profile: governance.scan
    config:
      check: impl.library_usage_non_regression
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
      - impl.library_usage_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
