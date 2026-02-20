# Governance Cases

## DCGOV-STDLIB-002

```yaml contract-spec
id: DCGOV-STDLIB-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: spec-lang stdlib symbols are parity-clean across python and php
purpose: Ensures no profile symbol is missing in either runtime implementation.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: spec_lang.stdlib_py_php_parity
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
