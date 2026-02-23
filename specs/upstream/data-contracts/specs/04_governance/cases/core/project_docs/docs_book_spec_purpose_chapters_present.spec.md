```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    docs_manifest:
      path: /docs/book/reference_manifest.yaml
      required_paths:
      - /docs/book/05_what_is_data_contracts.md
      - /docs/book/15_spec_lifecycle.md
      - /docs/book/25_system_topology.md
      - /docs/book/35_usage_guides_index.md
    check:
      profile: governance.scan
      config:
        check: docs.book_spec_purpose_chapters_present
contracts:
  clauses:
  - id: DCGOV-DOCS-REF-019
    title: spec purpose narrative chapters are present
    purpose: Ensures the core spec-purpose chapters are present in the reference manifest.
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
  - id: act.gov.docs.book.spec.purpose.c.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.book.spec.purpose.c.1
  consumes:
  - act.gov.docs.book.spec.purpose.c.1
```
