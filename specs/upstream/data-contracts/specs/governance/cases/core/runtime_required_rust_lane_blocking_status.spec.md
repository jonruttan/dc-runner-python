# Governance Cases

## DCGOV-RUNTIME-CONFIG-006

```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-006
title: required rust lane remains blocking
purpose: Ensures the required CI gate lane is rust-first and not configured as non-blocking.
type: contract.check
harness:
  root: .
  required_rust_lane:
    workflow: /.github/workflows/ci.yml
    required_tokens:
    - ci-gate: null
    - Run CI gate (required rust lane)
    - run: ./scripts/ci_gate.sh
    forbidden_tokens:
    - Run CI gate (diagnostic lane)
    - "continue-on-error: true\n        run: ./scripts/ci_gate.sh"
  check:
    profile: governance.scan
    config:
      check: runtime.required_rust_lane_blocking_status
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
