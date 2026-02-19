# Governance Cases

## DCGOV-ASSERT-PROFILE-001

```yaml contract-spec
id: DCGOV-ASSERT-PROFILE-001
title: subject profile contract artifacts are declared
purpose: Ensures subject profile contract/schema/type docs and domain libraries are present
  as required artifacts.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: assert.subject_profiles_declared
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
```
