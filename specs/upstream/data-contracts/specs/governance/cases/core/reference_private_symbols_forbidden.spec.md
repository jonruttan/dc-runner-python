```yaml contract-spec
id: DCGOV-REF-SYMBOLS-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: private library symbols are not referenced externally
purpose: Ensures conformance/governance/impl cases do not reference defines.private symbols
  from library docs.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: reference.private_symbols_forbidden
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
    - summary_json
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - reference.private_symbols_forbidden
```
