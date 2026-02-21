```yaml contract-spec
id: DCGOV-HARNESS-EXPORTS-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: harness exports schema is valid
purpose: Ensures harness.exports entries enforce as/from/path/params/required schema requirements.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.harness_exports_schema_valid
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
