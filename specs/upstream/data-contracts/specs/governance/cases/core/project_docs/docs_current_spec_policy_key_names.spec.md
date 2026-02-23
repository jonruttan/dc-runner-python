```yaml contract-spec
id: DCGOV-DOCS-CURRENT-KEYS-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: current spec policy key names stay canonical
purpose: Enforces policy expression naming consistency by allowing only `evaluate` in `.spec.md`
  cases.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.current_spec_policy_key_names
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
      - docs.current_spec_policy_key_names
    imports:
    - from: artifact
      names:
      - summary_json
```
