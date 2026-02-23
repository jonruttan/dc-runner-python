```yaml contract-spec
id: DCGOV-RUNTIME-STATUS-006
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: required lane status remains blocking
purpose: Ensures required-lane status outcomes map to blocking policy effects.
type: contract.check
harness:
  root: .
  required_lane_policy:
    path: /scripts/runner_status_ingest.sh
    required_tokens:
    - lane_class
    - required
    - blocking_fail
  check:
    profile: governance.scan
    config:
      check: runtime.required_lane_status_blocking_enforced
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
```

