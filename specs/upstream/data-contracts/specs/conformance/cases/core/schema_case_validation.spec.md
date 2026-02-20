# Schema Case Validation Conformance Cases

## DCCONF-SCHEMA-CASE-001

```yaml contract-spec
id: DCCONF-SCHEMA-CASE-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: valid core shape compiles and runs
purpose: Ensures standard top-level keys accepted by registry validation continue to execute
  successfully.
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
      std.string.contains:
      - {var: text}
      - Spec-Test Schema (v1)
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-SCHEMA-CASE-002

```yaml contract-spec
id: DCCONF-SCHEMA-CASE-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: unknown evaluate symbol is rejected as schema
purpose: Ensures unknown spec-lang symbols fail as schema in both runtimes.
type: contract.check
expect:
  portable:
    status: fail
    category: schema
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
      lit:
        unknown_symbol_for_schema_case:
        - var: text
harness:
  check:
    profile: text.file
    config: {}
```
