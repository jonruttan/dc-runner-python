```yaml contract-spec
id: DCGOV-SCHEMA-PIN-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec cases include schema_ref
purpose: Ensures schema pin validator enforces presence of schema_ref for all executable contract-spec blocks.
type: contract.check
harness:
  root: .
  schema_pin_validator:
    path: /scripts/spec_schema_pin_validate.sh
    required_tokens:
    - missing_schema_ref_count
  check:
    profile: governance.scan
    config:
      check: schema.spec_case_schema_ref_present
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
