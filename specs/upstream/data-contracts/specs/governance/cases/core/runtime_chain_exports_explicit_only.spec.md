# Governance Cases

## DCGOV-CHAIN-012

```yaml contract-spec
id: DCGOV-CHAIN-012
title: chain state sharing uses explicit exports only
purpose: Ensures chain state propagation is declared through explicit target-derived exports.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_exports_explicit_only
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
