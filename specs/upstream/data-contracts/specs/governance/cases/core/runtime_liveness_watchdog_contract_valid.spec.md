# Governance Cases

## DCGOV-LIVENESS-CONTRACT-001

```yaml contract-spec
id: DCGOV-LIVENESS-CONTRACT-001
title: runtime liveness watchdog contract docs and schema are synchronized
purpose: Ensures liveness controls and reason tokens are declared in runtime profiling contract
  and schema artifacts.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.liveness_watchdog_contract_valid
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
