```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    token_anchors:
      files:
      - path: /specs/02_contracts/03b_spec_lang_v1.md
        tokens:
        - operator-keyed mapping AST
    check:
      profile: governance.scan
      config:
        check: reference.token_anchors_exist
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
  - id: DCGOV-REF-TOKENS-001
    title: configured token anchors exist
    purpose: Ensures configured token anchors resolve to existing files and token
      matches.
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
          - reference.token_anchors_exist
adapters:
- type: beta.scan
  actions:
  - id: act.gov.reference.token.anchors.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.reference.token.anchors.1
  consumes:
  - act.gov.reference.token.anchors.1
```
