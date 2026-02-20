# Governance Cases

## DCGOV-REF-TOKENS-001

```yaml contract-spec
id: DCGOV-REF-TOKENS-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: configured token anchors exist
purpose: Ensures configured token anchors resolve to existing files and token matches.
type: contract.check
harness:
  root: .
  token_anchors:
    files:
    - path: /specs/contract/03b_spec_lang_v1.md
      tokens:
      - operator-keyed mapping AST
  check:
    profile: governance.scan
    config:
      check: reference.token_anchors_exist
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
      - reference.token_anchors_exist
```
