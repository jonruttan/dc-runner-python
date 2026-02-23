```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    contract_assertions_non_regression:
      baseline_path: /specs/04_governance/metrics/contract_assertions_baseline.json
      summary_fields:
        overall_contract_assertions_ratio: non_decrease
        overall_required_token_coverage_ratio: non_decrease
        contract_must_coverage_ratio: non_decrease
        token_sync_ratio: non_decrease
      epsilon: 1.0e-12
      contract_assertions:
        paths:
        - specs/02_contracts/03_assertions.md
        - specs/01_schema/schema_v1.md
        - docs/book/30_assertion_model.md
        - specs/02_contracts/03b_spec_lang_v1.md
    check:
      profile: governance.scan
      config:
        check: spec.contract_assertions_non_regression
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
  - id: DCGOV-CONTRACT-ASSERT-002
    title: contract assertions metric is non-regressing
    purpose: Enforces monotonic non-regression for contract assertions metrics against
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
          - spec.contract_assertions_non_regression
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.contract.assertions.non.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.contract.assertions.non.1
  consumes:
  - act.gov.contract.assertions.non.1
```
