# Governance Cases

## DCGOV-DOCS-REF-006

```yaml contract-spec
id: DCGOV-DOCS-REF-006
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: assertion tokens stay aligned across book contract and schema docs
purpose: Ensures core assertion terminology remains synchronized across author-facing and
  normative specification documents.
type: contract.check
harness:
  root: .
  doc_sync:
    files:
    - docs/book/30_assertion_model.md
    - specs/contract/03_assertions.md
    - specs/schema/schema_v1.md
    tokens:
    - MUST
    - MAY
    - MUST_NOT
    - contract.imports
  check:
    profile: governance.scan
    config:
      check: docs.contract_schema_book_sync
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
      - docs.contract_schema_book_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
