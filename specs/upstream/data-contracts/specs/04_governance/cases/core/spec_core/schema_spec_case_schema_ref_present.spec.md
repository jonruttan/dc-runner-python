```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    schema_pin_validator:
      path: /scripts/spec_schema_pin_validate.sh
      required_tokens:
      - missing_schema_ref_count
    check:
      profile: governance.scan
      config:
        check: schema.spec_case_schema_ref_present
contracts:
  clauses:
  - id: DCGOV-SCHEMA-PIN-002
    title: spec cases include schema_ref
    purpose: Ensures schema pin validator enforces presence of schema_ref for all
      executable contract-spec blocks.
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
  - id: act.gov.schema.spec.case.schema.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.schema.spec.case.schema.1
  consumes:
  - act.gov.schema.spec.case.schema.1
```
