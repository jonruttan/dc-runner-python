# Governance Cases

## DCGOV-DOCS-LIBSYM-002

```yaml contract-spec
id: DCGOV-DOCS-LIBSYM-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: library symbol doc params stay in sync
purpose: Ensures harness.exports params match doc.params names and order.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.library_symbol_params_sync
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
      - docs.library_symbol_params_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
