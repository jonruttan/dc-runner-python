# Governance Cases

## DCGOV-DOC-SEC-001

```yaml contract-spec
id: DCGOV-DOC-SEC-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: required trust-model docs declare non-sandboxed trusted-input contract
purpose: Ensures required docs state that spec execution is not sandboxed and untrusted specs
  are unsafe.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.security_warning_contract
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
      - docs.security_warning_contract
    imports:
    - from: artifact
      names:
      - summary_json
```
