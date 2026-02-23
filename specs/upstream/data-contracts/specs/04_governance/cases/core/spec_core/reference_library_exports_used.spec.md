```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    check:
      profile: governance.scan
      config:
        check: reference.library_exports_used
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
  - id: DCGOV-REF-SYMBOLS-003
    title: library exports are referenced
    purpose: Ensures exported library symbols are referenced by case policies/expressions
      or harness exports.
    asserts:
      imports:
      - from: asset
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - reference.library_exports_used
adapters:
- type: beta.scan
  actions:
  - id: act.gov.reference.library.export.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.reference.library.export.1
  consumes:
  - act.gov.reference.library.export.1
```
