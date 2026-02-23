```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-BUNDLE-001
    title: v1 schema docs forbid bundle suite metadata in contract-spec shape
    purpose: Ensures schema_v1 does not define top-level bundle metadata on executable
      suites.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.logic.and:
          - std.logic.not:
            - std.string.contains:
              - var: text
              - "- `bundle` (mapping, optional)"
          - std.logic.not:
            - std.string.contains:
              - var: text
              - "- `bundle.bundle_version` (string, optional)"
          - std.logic.not:
            - std.string.contains:
              - var: text
              - "- `bundle.maintainers` (list, optional)"
  - id: DCCONF-BUNDLE-002
    title: v1 core registry excludes bundle taxonomy fields
    purpose: Ensures schema registry v1 core profile does not codify top-level bundle
      mappings.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.logic.and:
          - std.logic.not:
            - std.string.contains:
              - var: text
              - 'bundle:'
          - std.logic.not:
            - std.string.contains:
              - var: text
              - 'bundle.bundle_version:'
          - std.logic.not:
            - std.string.contains:
              - var: text
              - 'bundle.domains[].modules[].artifacts[].kind:'
adapters:
- type: io.fs
  defaults:
    direction: input
    profile: read.text
  actions:
  - id: svc.assert_check.text_file.1
    config:
      source_asset_id: art.svc.assert_check.text_file.1.source.1
  - id: svc.assert_check.text_file.2
    config:
      source_asset_id: art.svc.assert_check.text_file.2.source.1
services:
- id: svc.assert_check.text_file.1
  consumes:
  - svc.assert_check.text_file.1
- id: svc.assert_check.text_file.2
  consumes:
  - svc.assert_check.text_file.2
assets:
- id: art.svc.assert_check.text_file.1.source.1
  ref: "/specs/01_schema/schema_v1.md"
- id: art.svc.assert_check.text_file.2.source.1
  ref: "/specs/01_schema/registry/v1/core.yaml"
```
