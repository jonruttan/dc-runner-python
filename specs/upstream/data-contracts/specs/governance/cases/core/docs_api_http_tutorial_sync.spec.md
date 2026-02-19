# Governance Cases

## DCGOV-DOCS-APIHTTP-001

```yaml contract-spec
id: DCGOV-DOCS-APIHTTP-001
title: api.http tutorials remain present in howto and troubleshooting docs
purpose: Ensures contributor docs cover practical REST verbs, CORS preflight, and round-trip
  scenario guidance.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.api_http_tutorial_sync
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
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.api_http_tutorial_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
