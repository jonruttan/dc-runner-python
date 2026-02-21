```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-008
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: compatibility matrix registration is explicit
purpose: Ensures runtime lanes are registered in the compatibility matrix contract before
  use.
type: contract.check
harness:
  root: .
  compatibility_matrix:
    path: /specs/contract/25_compatibility_matrix.md
    required_tokens:
    - '- `required`:'
    - '- `compatibility_non_blocking`:'
    - '- `rust`'
    - '- `python`'
    - '- `php`'
    - '- `node`'
    - '- `c`'
  check:
    profile: governance.scan
    config:
      check: runtime.compatibility_matrix_registration_required
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
