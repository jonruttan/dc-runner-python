```yaml contract-spec
id: DCGOV-NORM-PATHS-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: scoped spec paths use canonical virtual-root form
purpose: Ensures path-bearing spec fields use canonical virtual-root `/...` form.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: normalization.virtual_root_paths_only
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
    - summary_json
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - normalization.virtual_root_paths_only
```
