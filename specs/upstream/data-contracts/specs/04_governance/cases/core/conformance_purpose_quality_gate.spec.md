```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    purpose_quality:
      cases: specs/03_conformance/cases
      max_total_warnings: 0
      fail_on_policy_errors: true
      fail_on_severity: warn
    check:
      profile: governance.scan
      config:
        check: conformance.purpose_quality_gate
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
  - id: DCGOV-CONF-PURPOSE-002
    title: conformance purpose quality remains warning free
    purpose: Ensures conformance purpose lint policy and case purpose text stay clean
      with no accumulated warning debt.
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
          - conformance.purpose_quality_gate
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.conformance.purpose.qual.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.conformance.purpose.qual.1
  consumes:
  - act.gov.conformance.purpose.qual.1
```
