# Governance Cases

## DCGOV-SCHEMA-PIN-005

```yaml contract-spec
id: DCGOV-SCHEMA-PIN-005
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: schema catalog includes active contract-spec v1
purpose: Ensures active schema catalog includes canonical contract-spec v1 entry.
type: contract.check
harness:
  root: .
  schema_catalog:
    path: /specs/schema/schema_catalog_v1.yaml
    required_tokens:
    - schema_id: contract_spec
    - major: 1
    - path: /specs/schema/schema_v1.md
    - status: active
  check:
    profile: governance.scan
    config:
      check: schema.catalog_contains_active_schema_v1
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
