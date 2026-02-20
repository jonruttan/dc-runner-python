# Governance Cases

## DCGOV-REF-PATHS-001

```yaml contract-spec
id: DCGOV-REF-PATHS-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: contract paths referenced by specs exist
purpose: Ensures referenced contract-root paths fail fast when missing.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: reference.contract_paths_exist
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
      - reference.contract_paths_exist
```
