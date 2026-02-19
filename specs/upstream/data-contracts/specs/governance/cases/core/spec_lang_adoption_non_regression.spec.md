# Governance Cases

## DCGOV-SPEC-LANG-002

```yaml contract-spec
id: DCGOV-SPEC-LANG-002
title: spec-lang adoption metric is non-regressing
purpose: Enforces monotonic non-regression for spec-lang adoption metrics against checked-in
  baseline.
type: contract.check
harness:
  root: .
  spec_lang_adoption_non_regression:
    baseline_path: /specs/governance/metrics/spec_lang_adoption_baseline.json
    summary_fields:
      overall_logic_self_contained_ratio: non_decrease
      native_logic_escape_case_ratio: non_increase
      governance_library_backed_policy_ratio: non_decrease
      governance_symbol_resolution_ratio: non_decrease
      library_public_surface_ratio: non_decrease
    segment_fields:
      conformance:
        mean_logic_self_contained_ratio: non_decrease
      governance:
        mean_logic_self_contained_ratio: non_decrease
        library_backed_policy_ratio: non_decrease
        governance_symbol_resolution_ratio: non_decrease
    epsilon: 1.0e-12
    spec_lang_adoption:
      roots:
      - /specs/conformance/cases
      - /specs/governance/cases
      - runner-owned implementation specs
      segment_rules:
      - prefix: specs/conformance/cases
        segment: conformance
      - prefix: specs/governance/cases
        segment: governance
      - prefix: runner-owned implementation specs
        segment: impl
      recursive: true
  check:
    profile: governance.scan
    config:
      check: spec.spec_lang_adoption_non_regression
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
      - spec.spec_lang_adoption_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
