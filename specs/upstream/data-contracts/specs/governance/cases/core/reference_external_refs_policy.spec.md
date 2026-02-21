```yaml contract-spec
id: DCGOV-REF-EXTERNAL-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: external refs require explicit policy and capability
purpose: Ensures external:// references are deny-by-default and must declare allow policy.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: reference.external_refs_policy
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
      - reference.external_refs_policy
```
