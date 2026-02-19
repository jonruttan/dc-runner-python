# Governance Cases

## DCGOV-SCHEMA-VERB-001

```yaml contract-spec
id: DCGOV-SCHEMA-VERB-001
title: verb-first contract wording remains synchronized
purpose: Ensures schema/contract/current docs use defines wording and reject non-canonical
  definitions wording.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.verb_first_contract_sync
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
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - schema.verb_first_contract_sync
```
