# Governance Cases

## DCGOV-RUNTIME-CONFIG-007

```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-007
title: compatibility lanes remain non-blocking
purpose: Ensures compatibility runtime lanes are present in CI and explicitly non-blocking.
type: contract.check
harness:
  root: .
  compatibility_lanes:
    workflow: /.github/workflows/ci.yml
    required_tokens:
    - compatibility-python-lane: null
    - compatibility-php-lane: null
    - compatibility-node-lane: null
    - compatibility-c-lane: null
    - continue-on-error: true
  check:
    profile: governance.scan
    config:
      check: runtime.compatibility_lanes_non_blocking_status
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
