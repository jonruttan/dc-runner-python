# Governance Cases

## DCGOV-DOCS-MD-001

```yaml contract-spec
id: DCGOV-DOCS-MD-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: markdown checks use structured markdown helper library
purpose: Prevent brittle plain string-contains markdown assertions in governed docs cases.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.markdown_structured_assertions_required
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
      - docs.markdown_structured_assertions_required
    imports:
    - from: artifact
      names:
      - summary_json
```
