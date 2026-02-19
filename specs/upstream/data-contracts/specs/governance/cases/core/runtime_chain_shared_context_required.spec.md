# Governance Cases

## DCGOV-CHAIN-011

```yaml contract-spec
id: DCGOV-CHAIN-011
title: chain shared context is declared in dispatcher
purpose: Ensures chain state, trace, imports, and chain payload surfaces are carried in shared
  runtime context.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_shared_context_required
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
