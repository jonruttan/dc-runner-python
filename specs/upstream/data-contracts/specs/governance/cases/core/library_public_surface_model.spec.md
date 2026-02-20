# Governance Cases

## DCGOV-LIB-SURFACE-001

```yaml contract-spec
id: DCGOV-LIB-SURFACE-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: library public/private surface model is enforced
purpose: Ensures spec_lang.export cases use defines.public/defines.private scopes and do not
  use non-canonical export shape.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: library.public_surface_model
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
      - library.public_surface_model
```
