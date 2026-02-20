# Governance Cases

## DCGOV-RUNTIME-SCOPE-001

```yaml contract-spec
id: DCGOV-RUNTIME-SCOPE-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: runtime support scope remains bounded for v1
purpose: Prevents uncontrolled cross-runtime expansion by enforcing explicit v1 runtime scope
  tokens in contract docs.
type: contract.check
harness:
  root: .
  runtime_scope:
    files:
    - specs/contract/08_v1_scope.md
    - specs/contract/13_runtime_scope.md
    - specs/contract/12_runner_interface.md
    required_tokens:
    - Python runner
    - PHP runner
    - required support targets
    - contract/governance expansion
    forbidden_tokens:
    - Node.js runner
    - Ruby runner
    - Java runner
  check:
    profile: governance.scan
    config:
      check: runtime.scope_sync
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
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - runtime.scope_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
