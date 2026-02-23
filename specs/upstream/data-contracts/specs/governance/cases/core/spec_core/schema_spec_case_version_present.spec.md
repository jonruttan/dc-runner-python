```yaml contract-spec
id: DCGOV-SCHEMA-PIN-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec cases include spec_version
purpose: Ensures schema pin validator enforces presence of spec_version for all executable contract-spec blocks.
type: contract.check
harness:
  root: .
  schema_pin_validator:
    path: /scripts/spec_schema_pin_validate.sh
    required_tokens:
    - missing_spec_version_count
  check:
    profile: governance.scan
    config:
      check: schema.spec_case_version_present
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
