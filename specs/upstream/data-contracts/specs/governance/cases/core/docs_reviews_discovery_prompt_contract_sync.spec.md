# Governance Cases

## DCGOV-DOCS-REF-017

```yaml contract-spec
id: DCGOV-DOCS-REF-017
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: discovery review prompt remains contract-synced
purpose: Ensures the discovery-fit prompt references canonical review schema/contracts, required output sections, ordered entrypoint discovery, and explicit self-heal boundaries.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.reviews_discovery_prompt_contract_sync
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
      - docs.reviews_discovery_prompt_contract_sync
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
