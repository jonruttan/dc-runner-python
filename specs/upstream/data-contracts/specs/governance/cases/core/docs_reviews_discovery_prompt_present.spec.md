# Governance Cases

## DCGOV-DOCS-REF-016

```yaml contract-spec
id: DCGOV-DOCS-REF-016
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: discovery review prompt is present
purpose: Ensures the discovery-fit self-heal review prompt exists in the canonical active review prompt set.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.reviews_discovery_prompt_present
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
      - docs.reviews_discovery_prompt_present
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
