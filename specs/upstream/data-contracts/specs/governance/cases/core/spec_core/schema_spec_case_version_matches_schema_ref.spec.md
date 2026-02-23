```yaml contract-spec
id: DCGOV-SCHEMA-PIN-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec_version matches schema_ref major
purpose: Ensures schema pin validator rejects mismatched spec_version and schema_ref major values.
type: contract.check
harness:
  root: .
  schema_pin_validator:
    path: /scripts/spec_schema_pin_validate.sh
    required_tokens:
    - mismatched_version_count
  check:
    profile: governance.scan
    config:
      check: schema.spec_case_version_matches_schema_ref
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
