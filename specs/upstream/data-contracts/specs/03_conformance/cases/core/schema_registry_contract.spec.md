```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-REG-001
    title: schema docs include generated registry snapshot markers
    purpose: Ensures generated schema registry snapshot markers and section header
      are present in schema_v1 documentation.
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
        - call:
          - var: policy.text.contains_all
          - var: text
          - lit:
            - 'BEGIN GENERATED: SCHEMA_REGISTRY_V1'
            - 'END GENERATED: SCHEMA_REGISTRY_V1'
            - Generated Registry Snapshot
adapters:
- type: io.fs
  actions:
  - id: svc.check.text_file.1
    config:
      use:
      - as: lib_policy_text
        symbols:
        - policy.text.contains_all
        artifact_id: art.svc.check.text_file.1.use_1.1
      source_asset_id: art.svc.check.text_file.1.source.1
    direction: input
    profile: read.text
services:
- id: svc.check.text_file.1
  consumes:
  - svc.check.text_file.1
assets:
- id: art.svc.check.text_file.1.source.1
  ref: "/specs/01_schema/schema_v1.md"
- id: art.svc.check.text_file.1.use_1.1
  ref: "/specs/05_libraries/policy/policy_text.spec.md"
```
