# Conformance Cases

## DCCONF-SCHEMA-STDLIB-003

```yaml contract-spec
id: DCCONF-SCHEMA-STDLIB-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: json parsing and type predicates stay deterministic
purpose: Ensures parsed JSON shapes can be validated with deterministic type predicates.
type: contract.check
expect:
  portable:
    status: pass
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
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
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_schema.spec.md
```

## DCCONF-SCHEMA-STDLIB-004

```yaml contract-spec
id: DCCONF-SCHEMA-STDLIB-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: parsed payload predicates support deterministic error-shape checks
purpose: Ensures JSON payload predicate composition remains deterministic for invalid-value
  checks.
type: contract.check
expect:
  portable:
    status: pass
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
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
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_schema.spec.md
```
