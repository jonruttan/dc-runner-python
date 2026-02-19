# Governance Cases

## DCGOV-SCHEMA-REG-004

```yaml contract-spec
id: DCGOV-SCHEMA-REG-004
title: schema contract avoids prose-only rules
purpose: Ensures schema contract docs explicitly tie behavior to registry source-of-truth
  wording.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.no_prose_only_rules
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
      - schema.no_prose_only_rules
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
