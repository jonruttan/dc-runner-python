# Governance Cases

## DCGOV-RUNTIME-CERT-005

```yaml contract-spec
id: DCGOV-RUNTIME-CERT-005
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: compatibility lanes remain non-blocking in certification
purpose: Ensures compatibility lanes are classified and emitted as non-blocking in certification artifacts.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.runner_certification_compat_lanes_non_blocking
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
