```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    schema_catalog:
      path: /specs/01_schema/schema_catalog_v1.yaml
      required_tokens:
      - schema_id: contract_spec
      - major: 2
      - path: /specs/01_schema/schema_v1.md
      - status: active
    check:
      profile: governance.scan
      config:
        check: schema.catalog_contains_active_schema_v1
contracts:
  clauses:
  - id: DCGOV-SCHEMA-PIN-005
    title: schema catalog includes active contract-spec v1
    purpose: Ensures active schema catalog includes canonical contract-spec v1 entry.
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
adapters:
- type: beta.scan
  actions:
  - id: act.gov.schema.catalog.contains.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.schema.catalog.contains.1
  consumes:
  - act.gov.schema.catalog.contains.1
```
