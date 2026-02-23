```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    portability_non_regression:
      baseline_path: /specs/04_governance/metrics/spec_portability_baseline.json
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
        - /specs/04_governance/cases
        - external runner spec repository specs
        core_types:
        - text.file
        - cli.run
        segment_rules:
        - prefix: specs/03_conformance/cases
          segment: conformance
        - prefix: specs/04_governance/cases
          segment: governance
        - prefix: external runner spec repository specs
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
    - ref: /specs/05_libraries/policy/policy_assertions.spec.md
      as: lib_policy_core_spec
      symbols:
      - policy.assert.no_violations
      - policy.assert.summary_passed
      - policy.assert.summary_check_id
      - policy.assert.scan_pass
contracts:
  clauses:
  - id: DCGOV-SPEC-PORT-002
    title: spec-lang self-containment metric is non-regressing
    purpose: Enforces a monotonic ratchet so configured spec-lang self-containment
      metrics cannot decrease from baseline.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
      - id: assert_2
        assert:
        - call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
        - call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - spec.portability_non_regression
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.spec.portability.non.reg.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.spec.portability.non.reg.1
  consumes:
  - act.gov.spec.portability.non.reg.1
```
