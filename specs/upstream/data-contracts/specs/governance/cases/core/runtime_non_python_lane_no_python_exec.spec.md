```yaml contract-spec
id: DCGOV-RUNTIME-PYDEP-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: non-python lanes avoid direct python execution tokens
purpose: Ensures default gate/orchestration and rust adapter lane files do not contain python
  execution tokens.
type: contract.check
harness:
  root: .
  python_dependency: {}
  check:
    profile: governance.scan
    config:
      check: runtime.non_python_lane_no_python_exec
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
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - runtime.non_python_lane_no_python_exec
    imports:
    - from: artifact
      names:
      - summary_json
```
