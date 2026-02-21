```yaml contract-spec
id: DCGOV-CHAIN-005
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: chain template references resolve against explicit exports
purpose: Ensures api.http chain templates use declared step export names and fail on unresolved
  references.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_state_template_resolution
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
