# Governance Cases

## DCGOV-DOCS-GEN-021

```yaml contract-spec
id: DCGOV-DOCS-GEN-021
title: stdlib symbols include semantic docs payload
purpose: Ensures every stdlib symbol has summary, params, returns, errors, and examples in
  generated catalogs.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.stdlib_symbol_docs_complete
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
      - docs.stdlib_symbol_docs_complete
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
