# Governance Cases

## DCGOV-CHAIN-009

```yaml contract-spec
id: DCGOV-CHAIN-009
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: chain contract uses harness.chain only
purpose: Ensures chain declarations appear only at harness.chain and not in alternate top-level
  or type-specific locations.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_contract_single_location
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
