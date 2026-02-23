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
        check: runtime.chain_imports_consumer_surface_unchanged
contracts:
  clauses:
  - id: DCGOV-HARNESS-EXPORTS-004
    title: chain imports consumer surface remains unchanged
    purpose: Ensures consumer bindings continue to use harness.chain.imports semantics.
    asserts:
      imports:
      - from: asset
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.chain.imports.co.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.chain.imports.co.1
  consumes:
  - act.gov.runtime.chain.imports.co.1
```
