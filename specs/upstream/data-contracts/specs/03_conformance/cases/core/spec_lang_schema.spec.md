```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-STDLIB-003
    title: json parsing and type predicates stay deterministic
    purpose: Ensures parsed JSON shapes can be validated with deterministic type predicates.
    expect:
      portable:
        status: pass
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - std.logic.eq:
          - std.type.json_type:
            - std.json.parse:
              - '{"id":1,"tags":["alpha","beta"]}'
            - dict
          - true
        - std.logic.eq:
          - std.type.json_type:
            - std.object.get:
              - std.json.parse:
                - '{"id":1,"tags":["alpha","beta"]}'
              - tags
            - list
          - true
  - id: DCCONF-SCHEMA-STDLIB-004
    title: parsed payload predicates support deterministic error-shape checks
    purpose: Ensures JSON payload predicate composition remains deterministic for
      invalid-value checks.
    expect:
      portable:
        status: pass
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.logic.and:
          - std.logic.eq:
            - std.type.json_type:
              - std.object.get:
                - std.json.parse:
                  - '{"id":"x"}'
                - id
              - string
            - true
          - std.logic.not:
            - std.logic.eq:
              - std.object.get:
                - std.json.parse:
                  - '{"id":"x"}'
                - id
              - 1
adapters:
- type: io.fs
  actions:
  - id: svc.assert_check.text_file.1
    config:
      source_asset_id: art.svc.assert_check.text_file.1.source.1
    direction: input
    profile: read.text
services:
- id: svc.assert_check.text_file.1
  consumes:
  - svc.assert_check.text_file.1
assets:
- id: art.svc.assert_check.text_file.1.source.1
  ref: "/specs/03_conformance/cases/core/spec_lang_schema.spec.md"
```


