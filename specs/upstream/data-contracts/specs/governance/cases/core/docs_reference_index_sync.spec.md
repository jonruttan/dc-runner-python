# Governance Cases

## DCGOV-DOCS-REF-002

```yaml contract-spec
id: DCGOV-DOCS-REF-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: reference index stays synced with chapter files
purpose: Ensures the machine-checked reference index entries stay aligned with the actual
  chapter set and order.
type: contract.check
harness:
  root: .
  reference_index:
    path: /docs/book/reference_index.md
    include_glob: docs/book/*.md
    exclude_files:
    - docs/book/index.md
    - docs/book/reference_index.md
    - docs/book/reference_coverage.md
  check:
    profile: governance.scan
    config:
      check: docs.reference_index_sync
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
      - docs.reference_index_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
