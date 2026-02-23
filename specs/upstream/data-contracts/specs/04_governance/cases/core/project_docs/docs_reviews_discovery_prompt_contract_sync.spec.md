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
        check: docs.reviews_discovery_prompt_contract_sync
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
  - id: DCGOV-DOCS-REF-017
    title: discovery review prompt remains contract-synced
    purpose: Ensures the discovery-fit prompt references canonical review schema/contracts,
      required output sections, ordered entrypoint discovery, and explicit self-heal
      boundaries.
    asserts:
      imports:
      - from: asset
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - docs.reviews_discovery_prompt_contract_sync
        - call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.reviews.discovery.p.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.reviews.discovery.p.1
  consumes:
  - act.gov.docs.reviews.discovery.p.1
```
