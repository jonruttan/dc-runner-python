# Governance Cases

## DCGOV-DOC-CURRENT-001

```yaml contract-spec
id: DCGOV-DOC-CURRENT-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: current-spec-only contract forbids prior-schema references and shims
purpose: Ensures pre-v1 docs and parser paths stay focused on current schema only, without
  prior-spec wording or compatibility rewrites.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.current_spec_only_contract
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
      - docs.current_spec_only_contract
    imports:
    - from: artifact
      names:
      - summary_json
```
