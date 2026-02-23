```yaml contract-spec
id: DCGOV-DOCS-GEN-023
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: harness reference includes semantic sections
purpose: Ensures generated harness reference includes summary/defaults/failure modes/examples
  per case type.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.harness_reference_semantics_complete
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
      - docs.harness_reference_semantics_complete
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
