```yaml contract-spec
id: DCGOV-DOCS-LAYOUT-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: docs tree excludes OS/editor artifact files
purpose: Prevents tracked filesystem artifacts (for example .DS_Store) in docs surfaces.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.no_os_artifact_files
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
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.no_os_artifact_files
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
