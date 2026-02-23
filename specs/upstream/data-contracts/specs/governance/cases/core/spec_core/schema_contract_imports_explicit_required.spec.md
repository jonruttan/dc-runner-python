```yaml contract-spec
id: DCGOV-SCHEMA-CONTRACT-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: contract assertions require explicit imports
purpose: Ensures cases using var subject define imports.subject via contract imports or step
  imports.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.contract_imports_explicit_required
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
