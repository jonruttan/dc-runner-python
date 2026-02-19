# Governance Cases

## DCGOV-RUNTIME-APIHTTP-007

```yaml contract-spec
id: DCGOV-RUNTIME-APIHTTP-007
title: api.http scenario roundtrip support remains present
purpose: Ensures requests-list roundtrip support, step templating, and steps_json targeting
  remain implemented.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.api_http_scenario_roundtrip
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
      - runtime.api_http_scenario_roundtrip
    imports:
    - from: artifact
      names:
      - summary_json
```
