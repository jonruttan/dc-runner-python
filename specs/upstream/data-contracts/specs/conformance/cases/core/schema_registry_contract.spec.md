# Schema Registry Contract Conformance Cases

## DCCONF-SCHEMA-REG-001

```yaml contract-spec
id: DCCONF-SCHEMA-REG-001
title: schema docs include generated registry snapshot markers
purpose: Ensures generated schema registry snapshot markers and section header are present
  in schema_v1 documentation.
type: contract.check
expect:
  portable:
    status: pass
    category: null
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
    - std.string.contains:
      - {var: text}
      - 'BEGIN GENERATED: SCHEMA_REGISTRY_V1'
    - std.string.contains:
      - {var: text}
      - 'END GENERATED: SCHEMA_REGISTRY_V1'
    - std.string.contains:
      - {var: text}
      - Generated Registry Snapshot
harness:
  check:
    profile: text.file
    config:
      path: /specs/schema/schema_v1.md
```
