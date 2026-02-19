# Governance Cases

## DCGOV-DOCS-SPECCASE-001

```yaml contract-spec
id: DCGOV-DOCS-SPECCASE-001
title: spec case root doc metadata is complete
purpose: Ensures contract.export cases declare required root doc metadata fields.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.spec_case_doc_metadata_complete
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
      - docs.spec_case_doc_metadata_complete
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
