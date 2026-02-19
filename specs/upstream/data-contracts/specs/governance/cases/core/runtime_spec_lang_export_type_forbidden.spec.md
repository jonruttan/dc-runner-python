# Governance Cases

## DCGOV-RUNTIME-SPECLANG-EXPORT-001

```yaml contract-spec
id: DCGOV-RUNTIME-SPECLANG-EXPORT-001
title: non-canonical spec_lang.export type is forbidden after hard cut
purpose: Ensures executable spec surfaces reject type spec_lang.export and require spec.export
  producer cases.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.spec_lang_export_type_forbidden
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
      - runtime.spec_lang_export_type_forbidden
    imports:
    - from: artifact
      names:
      - summary_json
```
