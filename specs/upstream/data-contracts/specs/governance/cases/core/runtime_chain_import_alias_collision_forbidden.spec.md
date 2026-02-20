# Governance Cases

## DCGOV-CHAIN-008

```yaml contract-spec
id: DCGOV-CHAIN-008
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: chain import alias collisions are forbidden
purpose: Ensures harness.chain.imports bindings are valid and do not collide or shadow reserved
  symbols.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_import_alias_collision_forbidden
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
