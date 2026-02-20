# Governance Cases

## DCGOV-CONTRACT-001

```yaml contract-spec
id: DCGOV-CONTRACT-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: contract governance rules pass via governance harness
purpose: Ensures contract policy and traceability integrity checks are enforced through the
  governance spec pipeline.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: contract.governance_check
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
      - contract.governance_check
    imports:
    - from: artifact
      names:
      - summary_json
```
