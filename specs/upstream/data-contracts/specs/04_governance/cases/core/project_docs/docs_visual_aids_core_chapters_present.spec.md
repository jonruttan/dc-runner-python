```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    docs_quality_contract:
      path: /specs/02_contracts/10_docs_quality.md
      required_tokens:
      - 05_what_is_data_contracts.md
      - 15_spec_lifecycle.md
      - 25_system_topology.md
      - Mermaid diagram block
    check:
      profile: governance.scan
      config:
        check: docs.visual_aids_core_chapters_present
contracts:
  clauses:
  - id: DCGOV-DOCS-REF-022
    title: visual aids required in core chapters
    purpose: Ensures docs quality contract enforces Mermaid visual aid requirements
      for core narrative chapters.
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
  - id: act.gov.docs.visual.aids.core.ch.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.visual.aids.core.ch.1
  consumes:
  - act.gov.docs.visual.aids.core.ch.1
```
