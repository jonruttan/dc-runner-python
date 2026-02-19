# Governance Cases

## DCGOV-RUNTIME-CERT-004

```yaml contract-spec
id: DCGOV-RUNTIME-CERT-004
title: required rust runner certification lane passes
purpose: Ensures rust required lane certification passes and remains blocking.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.runner_certification_required_lane_passes
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
