```yaml contract-spec
id: DCGOV-DOCS-GEN-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: generated markdown sections are read-only blocks
purpose: Ensures configured generated markdown outputs contain valid generated section markers.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.generated_sections_read_only
  use:
  - ref: /specs/05_libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
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
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.generated_sections_read_only
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
