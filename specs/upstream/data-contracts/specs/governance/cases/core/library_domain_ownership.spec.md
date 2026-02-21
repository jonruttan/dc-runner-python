```yaml contract-spec
id: DCGOV-LIB-DOMAIN-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: library paths obey domain ownership
purpose: Ensures conformance cases use conformance libraries and governance cases use policy/path
  libraries.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: library.domain_ownership
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
      - library.domain_ownership
```
