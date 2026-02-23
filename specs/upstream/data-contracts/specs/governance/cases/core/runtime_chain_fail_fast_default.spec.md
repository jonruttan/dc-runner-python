```yaml contract-spec
id: DCGOV-CHAIN-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: chain fail_fast defaults stay canonical
purpose: Ensures harness.chain fail_fast and allow_continue fields preserve bool/default contracts.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_fail_fast_default
  use:
  - ref: /specs/05_libraries/policy/policy_core.spec.md
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
