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
      - mismatched_version_count
    check:
      profile: governance.scan
      config:
        check: schema.spec_case_version_matches_schema_ref
contracts:
  clauses:
  - id: DCGOV-SCHEMA-PIN-004
    title: spec_version matches schema_ref major
    purpose: Ensures schema pin validator rejects mismatched spec_version and schema_ref
      major values.
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
  - id: act.gov.schema.spec.case.version.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.schema.spec.case.version.1
  consumes:
  - act.gov.schema.spec.case.version.1
```
