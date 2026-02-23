```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    docs_quality:
      manifest: docs/book/reference_manifest.yaml
    check:
      profile: governance.scan
      config:
        check: docs.meta_schema_valid
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
  - id: DCGOV-DOCS-QUAL-001
    title: docs metadata schema is valid for canonical reference chapters
    purpose: Ensures each canonical reference chapter contains valid machine-checkable
      doc metadata.
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
      - id: assert_2
        assert:
        - call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
        - call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - docs.meta_schema_valid
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.meta.schema.valid.s.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.meta.schema.valid.s.1
  consumes:
  - act.gov.docs.meta.schema.valid.s.1
```
