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
        check: schema.verb_first_contract_sync
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
  - id: DCGOV-SCHEMA-VERB-001
    title: verb-first contract wording remains synchronized
    purpose: Ensures schema/contract/current docs use defines wording and reject canonical
      definitions wording.
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
          - schema.verb_first_contract_sync
adapters:
- type: beta.scan
  actions:
  - id: act.gov.schema.verb.first.contra.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.schema.verb.first.contra.1
  consumes:
  - act.gov.schema.verb.first.contra.1
```
