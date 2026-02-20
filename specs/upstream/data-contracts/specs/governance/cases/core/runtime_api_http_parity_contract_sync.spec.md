# Governance Cases

## DCGOV-RUNTIME-APIHTTP-008

```yaml contract-spec
id: DCGOV-RUNTIME-APIHTTP-008
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: api.http python/php parity contract surfaces remain synchronized
purpose: Ensures python/php api.http implementations and contracts expose shared v1 tokens.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.api_http_parity_contract_sync
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
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - runtime.api_http_parity_contract_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
