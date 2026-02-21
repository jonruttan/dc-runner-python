```yaml contract-spec
id: DCGOV-CHAIN-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: chain cycles are forbidden
purpose: Ensures direct and indirect harness.chain dependency cycles are rejected.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_cycle_forbidden
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
