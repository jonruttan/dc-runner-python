# Governance Cases

## DCGOV-RUNTIME-CONFIG-005

```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-005
title: python compatibility lane remains non-blocking
purpose: Ensures Python compatibility lane exists in CI and is configured as non-blocking.
type: contract.check
harness:
  root: .
  ci_python_lane_non_blocking:
    workflow: /.github/workflows/ci.yml
    required_tokens:
    - compatibility-python-lane: null
    - continue-on-error: true
    - Run Python compatibility lane (non-blocking)
    forbidden_tokens:
    - python-parity-lane: null
  check:
    profile: governance.scan
    config:
      check: runtime.ci_python_lane_non_blocking_required
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
