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
        check: reference.policy_symbols_resolve
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
  - id: DCGOV-REF-SYMBOLS-002
    title: governance policy symbols resolve through declared libraries
    purpose: Ensures every dotted var reference used in evaluate resolves from declared
      library symbols.
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
          - reference.policy_symbols_resolve
adapters:
- type: beta.scan
  actions:
  - id: act.gov.reference.policy.symbols.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.reference.policy.symbols.1
  consumes:
  - act.gov.reference.policy.symbols.1
```
