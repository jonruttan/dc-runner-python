```yaml contract-spec
id: DCGOV-SPEC-PORT-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec-lang self-containment metric is non-regressing
purpose: Enforces a monotonic ratchet so configured spec-lang self-containment metrics cannot
  decrease from baseline.
type: contract.check
harness:
  root: .
  portability_non_regression:
    baseline_path: /specs/governance/metrics/spec_portability_baseline.json
    summary_fields:
    - overall_logic_self_contained_ratio
    segment_fields:
      conformance:
      - mean_logic_self_contained_ratio
      governance:
      - mean_logic_self_contained_ratio
      impl:
      - mean_logic_self_contained_ratio
    epsilon: 1.0e-12
    portability_metric:
      roots:
      - /specs/03_conformance/cases
      - /specs/governance/cases
      - runner-owned implementation specs
      core_types:
      - text.file
      - cli.run
      segment_rules:
      - prefix: specs/conformance/cases
        segment: conformance
      - prefix: specs/governance/cases
        segment: governance
      - prefix: runner-owned implementation specs
        segment: impl
      runtime_capability_tokens:
      - api.http
      - governance.check
      runtime_capability_prefixes:
      - runtime.
      - php.
      - python.
      weights:
        non_evaluate_leaf_share: 0.45
        expect_impl_overlay: 0.25
        runtime_specific_capability: 0.15
        non_core_type: 0.15
      report:
        top_n: 10
      enforce: false
  check:
    profile: governance.scan
    config:
      check: spec.portability_non_regression
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
      - spec.portability_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
