```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    structured_assertions:
      cases_path: /specs/04_governance/cases
      case_file_pattern: '*.spec.md'
      ignore_checks:
      - governance.structured_assertions_required
    check:
      profile: governance.scan
      config:
        check: governance.structured_assertions_required
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
  - id: DCGOV-POLICY-REQ-003
    title: governance checks require structured assertion targets
    purpose: Ensures governance cases validate deterministic structured result targets
      instead of relying on PASS text markers as primary contract truth.
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
          - governance.structured_assertions_required
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.governance.structured.as.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.governance.structured.as.1
  consumes:
  - act.gov.governance.structured.as.1
```
