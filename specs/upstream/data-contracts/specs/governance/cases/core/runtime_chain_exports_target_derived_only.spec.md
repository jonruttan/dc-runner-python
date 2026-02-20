# Governance Cases

## DCGOV-CHAIN-003

```yaml contract-spec
id: DCGOV-CHAIN-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: chain exports remain target-derived only
purpose: Ensures harness.chain step exports declare only explicit target-derived extraction
  keys.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_exports_target_derived_only
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
