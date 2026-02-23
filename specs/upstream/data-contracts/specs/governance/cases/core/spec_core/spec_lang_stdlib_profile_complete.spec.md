```yaml contract-spec
id: DCGOV-STDLIB-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec-lang stdlib profile is complete
purpose: Ensures the declared stdlib profile symbols are implemented in Python and PHP.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: spec_lang.stdlib_profile_complete
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
```
