```yaml contract-spec
id: DCGOV-DOCS-GEN-007
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: policy rule catalog artifacts are synchronized
purpose: Ensures generated policy rule JSON and markdown artifacts are up-to-date.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.policy_rule_catalog_sync
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
      - docs.policy_rule_catalog_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
