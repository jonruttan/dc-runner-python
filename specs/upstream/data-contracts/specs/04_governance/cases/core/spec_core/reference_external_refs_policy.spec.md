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
        check: reference.external_refs_policy
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
  - id: DCGOV-REF-EXTERNAL-001
    title: external refs require explicit policy and capability
    purpose: Ensures external:// references are deny-by-default and must declare allow
      policy.
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
          - reference.external_refs_policy
adapters:
- type: beta.scan
  actions:
  - id: act.gov.reference.external.refs.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.reference.external.refs.1
  consumes:
  - act.gov.reference.external.refs.1
```
