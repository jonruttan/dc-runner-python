```yaml contract-spec
id: DCGOV-RUNTIME-HOOKS-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: when hooks schema must be valid
purpose: Enforces when shape and hook expression list requirements.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.when_hooks_schema_valid
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
