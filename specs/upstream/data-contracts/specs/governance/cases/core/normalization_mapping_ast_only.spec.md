```yaml contract-spec
id: DCGOV-NORM-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: normalization enforces mapping-ast-only expression authoring
purpose: Ensures expression-bearing YAML fields remain mapping-AST only and normalized through
  the unified normalize check.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: normalization.mapping_ast_only
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
      - normalization.mapping_ast_only
    imports:
    - from: artifact
      names:
      - summary_json
```
