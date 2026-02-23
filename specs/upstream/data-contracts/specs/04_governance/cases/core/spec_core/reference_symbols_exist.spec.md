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
        check: reference.symbols_exist
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
  - id: DCGOV-REF-SYMBOLS-001
    title: referenced library symbols resolve
    purpose: Ensures harness.spec_lang exports and library symbols resolve deterministically.
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
          - reference.symbols_exist
adapters:
- type: beta.scan
  actions:
  - id: act.gov.reference.symbols.exist.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.reference.symbols.exist.1
  consumes:
  - act.gov.reference.symbols.exist.1
```
