# Governance Cases

## DCGOV-DOCS-SPECDOMAIN-001

```yaml contract-spec
id: DCGOV-DOCS-SPECDOMAIN-001
title: spec case catalog domain grouping is synchronized
purpose: Ensures generated spec case catalog includes stable domain-grouped sections.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.spec_domain_grouping_sync
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
      - docs.spec_domain_grouping_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
