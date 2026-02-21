```yaml contract-spec
id: DCGOV-SPEC-MD-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: generated data artifacts do not embed executable spec blocks
purpose: Ensures machine-native yaml and json data artifact surfaces remain non-executable
  and do not contain yaml contract-spec fences.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: spec.generated_data_artifacts_not_embedded_in_spec_blocks
  use:
  - ref: /specs/libraries/policy/policy_core.spec.md
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
      - spec.generated_data_artifacts_not_embedded_in_spec_blocks
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
