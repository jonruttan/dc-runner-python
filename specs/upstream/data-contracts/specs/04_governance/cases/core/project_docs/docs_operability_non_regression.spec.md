```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    docs_operability_non_regression:
      baseline_path: /specs/04_governance/metrics/docs_operability_baseline.json
      summary_fields:
        overall_docs_operability_ratio: non_decrease
      segment_fields:
        book:
          mean_runnable_example_coverage_ratio: non_decrease
        contract:
          mean_token_sync_compliance_ratio: non_decrease
      epsilon: 1.0e-12
      docs_operability:
        reference_manifest: /docs/book/reference_manifest.yaml
    check:
      profile: governance.scan
      config:
        check: docs.operability_non_regression
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
  - id: DCGOV-DOCS-OPER-002
    title: docs operability metric is non-regressing
    purpose: Enforces monotonic non-regression for docs operability metrics against
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
          - docs.operability_non_regression
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.operability.non.reg.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.operability.non.reg.1
  consumes:
  - act.gov.docs.operability.non.reg.1
```
