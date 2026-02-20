# Governance Cases

## DCGOV-CONF-API-001

```yaml contract-spec
id: DCGOV-CONF-API-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: api.http portable conformance cases use canonical shape
purpose: Ensures api.http portable fixtures keep setup under harness and use only canonical
  behavior assertion targets.
type: contract.check
harness:
  root: .
  api_http:
    allowed_top_level_keys:
    - id
    - type
    - title
    - purpose
    - request
    - requests
    - assert
    - expect
    - requires
    - assert_health
    - harness
    allowed_assert_targets:
    - status
    - headers
    - body_text
    - body_json
    - cors_json
    - steps_json
    - context_json
    required_request_fields:
    - method
    - url
  check:
    profile: governance.scan
    config:
      check: conformance.api_http_portable_shape
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
      - conformance.api_http_portable_shape
    imports:
    - from: artifact
      names:
      - summary_json
```
