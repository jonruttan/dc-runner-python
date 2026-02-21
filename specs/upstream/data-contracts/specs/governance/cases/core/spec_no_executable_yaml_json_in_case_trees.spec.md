```yaml contract-spec
id: DCGOV-SPEC-MD-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: canonical executable trees forbid yaml and json case files
purpose: Ensures no runnable .spec.yaml, .spec.yml, or .spec.json files exist under canonical
  executable case roots.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: spec.no_executable_yaml_json_in_case_trees
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
      - spec.no_executable_yaml_json_in_case_trees
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
