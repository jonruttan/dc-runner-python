```yaml contract-spec
id: DCGOV-DOCS-GEN-024
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner reference includes semantic sections
purpose: Ensures generated runner API reference includes summary/defaults/failure modes/examples
  per command.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.runner_reference_semantics_complete
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
      - docs.runner_reference_semantics_complete
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
