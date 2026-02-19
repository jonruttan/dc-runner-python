# Governance Cases

## DCGOV-SPEC-MD-003

```yaml contract-spec
id: DCGOV-SPEC-MD-003
title: spec-lang library cases are markdown only
purpose: Ensures type spec_lang.export cases are authored only in .spec.md files under specs/libraries.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: spec.library_cases_markdown_only
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
      - spec.library_cases_markdown_only
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
