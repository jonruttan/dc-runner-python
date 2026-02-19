# Governance Cases

## DCGOV-CHAIN-001

```yaml contract-spec
id: DCGOV-CHAIN-001
title: chain references resolve deterministically
purpose: Ensures harness.chain step references resolve by contract for
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_reference_resolution
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
  - id: assert_2
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - runtime.chain_reference_resolution
    imports:
    - from: artifact
      names:
      - summary_json
```
