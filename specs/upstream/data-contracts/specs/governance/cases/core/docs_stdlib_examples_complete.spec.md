# Governance Cases

## DCGOV-DOCS-GEN-022

```yaml contract-spec
id: DCGOV-DOCS-GEN-022
title: stdlib symbols include examples
purpose: Ensures generated stdlib reference includes at least one complete example per symbol.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.stdlib_examples_complete
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
      - docs.stdlib_examples_complete
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
