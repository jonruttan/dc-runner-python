```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    spec_lang_adoption_non_regression:
      baseline_path: /specs/04_governance/metrics/spec_lang_adoption_baseline.json
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
        - /specs/03_conformance/cases
        - /specs/04_governance/cases
        - external runner spec repository specs
        segment_rules:
        - prefix: specs/03_conformance/cases
          segment: conformance
        - prefix: specs/04_governance/cases
          segment: governance
        - prefix: external runner spec repository specs
          segment: impl
        recursive: true
    check:
      profile: governance.scan
      config:
        check: spec.spec_lang_adoption_non_regression
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
  - id: DCGOV-SPEC-LANG-002
    title: spec-lang adoption metric is non-regressing
    purpose: Enforces monotonic non-regression for spec-lang adoption metrics against
      checked-in baseline.
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
          - spec.spec_lang_adoption_non_regression
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.spec.lang.adoption.non.r.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.spec.lang.adoption.non.r.1
  consumes:
  - act.gov.spec.lang.adoption.non.r.1
```
