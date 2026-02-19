# Governance Cases

## DCGOV-NORM-003

```yaml contract-spec
id: DCGOV-NORM-003
title: normalization docs token sync is enforced
purpose: Ensures schema contract and book docs maintain required mapping-AST wording and forbid
  stale expression-shape tokens.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: normalization.docs_token_sync
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
      - normalization.docs_token_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
