# Governance Cases

## DCGOV-IMPL-SPECLANG-002

```yaml contract-spec
id: DCGOV-IMPL-SPECLANG-002
title: impl evaluate-first ratio is non-regressing
purpose: Enforces ratchet-style non-regression for impl evaluate coverage against the checked-in
  spec-lang adoption baseline.
type: contract.check
harness:
  root: .
  impl_evaluate_first_non_regression:
    baseline_path: /specs/governance/metrics/spec_lang_adoption_baseline.json
    summary_fields:
      overall_logic_self_contained_ratio: non_decrease
    segment_fields:
      impl:
        mean_logic_self_contained_ratio: non_decrease
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
      check: impl.evaluate_ratio_non_regression
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
      - impl.evaluate_ratio_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
