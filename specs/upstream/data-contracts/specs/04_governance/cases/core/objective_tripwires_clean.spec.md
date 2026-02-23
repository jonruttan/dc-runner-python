```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    objective_tripwires:
      manifest_path: /specs/04_governance/metrics/objective_manifest.yaml
      cases_path: /specs/04_governance/cases
      case_file_pattern: '*.spec.md'
    check:
      profile: governance.scan
      config:
        check: objective.tripwires_clean
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
  - id: DCGOV-OBJECTIVE-003
    title: objective tripwires are clean
    purpose: Ensures objective manifest tripwire checks map to valid governance checks
      and currently pass.
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
          - objective.tripwires_clean
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.objective.tripwires.clea.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.objective.tripwires.clea.1
  consumes:
  - act.gov.objective.tripwires.clea.1
```
