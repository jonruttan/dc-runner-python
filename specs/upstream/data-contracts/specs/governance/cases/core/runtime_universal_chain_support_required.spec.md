```yaml contract-spec
id: DCGOV-CHAIN-010
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: universal chain support is present in dispatcher
purpose: Ensures all executable task types execute through shared harness.chain orchestration
  in dispatcher.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.universal_chain_support_required
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
