# Governance Cases

## DCGOV-RUNTIME-FAILFAST-003

```yaml contract-spec
id: DCGOV-RUNTIME-FAILFAST-003
title: gate failures emit profile artifacts when profile-on-fail is enabled
purpose: Ensures failure paths generate deterministic run-trace and run-trace-summary artifacts.
type: contract.check
harness:
  root: .
  profile_on_fail:
    files:
    - /dc-runner-python
    - /dc-runner-rust
    required_tokens:
    - profile-on-fail
    - .artifacts/run-trace.json
    - .artifacts/run-trace-summary.md
  check:
    profile: governance.scan
    config:
      check: runtime.profile_artifacts_on_fail_required
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
