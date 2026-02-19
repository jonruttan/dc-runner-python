# Governance Cases

## DCGOV-RUNTIME-PREPUSH-001

```yaml contract-spec
id: DCGOV-RUNTIME-PREPUSH-001
title: local ci parity script is rust-only
purpose: Ensures local prepush parity flow contains no python parity lane hooks.
type: contract.check
harness:
  root: .
  local_ci_parity_python_lane:
    path: /scripts/local_ci_parity.sh
    required_tokens:
    - MODE="${SPEC_PREPUSH_MODE:-critical}"
    - 'mode=critical: rust-only critical path'
    - expected critical|fast
    forbidden_tokens:
    - lane_python_parity
    - --impl python
    - SPEC_PREPUSH_MODE:-parity
    - python-governance-triage
  check:
    profile: governance.scan
    config:
      check: runtime.local_ci_parity_python_lane_forbidden
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
