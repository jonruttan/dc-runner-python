```yaml contract-spec
id: DCGOV-SPEC-MD-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: executable spec surfaces are markdown only
purpose: Ensures all canonical executable case trees are authored as .spec.md and do not use
  runnable yaml/json case files.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: spec.executable_surface_markdown_only
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
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - spec.executable_surface_markdown_only
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
