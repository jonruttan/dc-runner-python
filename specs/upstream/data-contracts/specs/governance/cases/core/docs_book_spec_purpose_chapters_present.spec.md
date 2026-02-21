```yaml contract-spec
id: DCGOV-DOCS-REF-019
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: spec purpose narrative chapters are present
purpose: Ensures the core spec-purpose chapters are present in the reference manifest.
type: contract.check
harness:
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
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
```
