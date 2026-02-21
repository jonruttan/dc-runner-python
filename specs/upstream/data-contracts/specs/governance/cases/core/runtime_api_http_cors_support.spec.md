```yaml contract-spec
id: DCGOV-RUNTIME-APIHTTP-006
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: api.http CORS support surfaces remain synchronized
purpose: Ensures CORS preflight and normalized cors_json projection are documented and implemented.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.api_http_cors_support
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
      - runtime.api_http_cors_support
    imports:
    - from: artifact
      names:
      - summary_json
```
