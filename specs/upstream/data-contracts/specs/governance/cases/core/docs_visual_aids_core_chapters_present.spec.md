```yaml contract-spec
id: DCGOV-DOCS-REF-022
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: visual aids required in core chapters
purpose: Ensures docs quality contract enforces Mermaid visual aid requirements for core narrative chapters.
type: contract.check
harness:
  root: .
  docs_quality_contract:
    path: /specs/contract/10_docs_quality.md
    required_tokens:
    - 05_what_is_data_contracts.md
    - 15_spec_lifecycle.md
    - 25_system_topology.md
    - Mermaid diagram block
  check:
    profile: governance.scan
    config:
      check: docs.visual_aids_core_chapters_present
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
