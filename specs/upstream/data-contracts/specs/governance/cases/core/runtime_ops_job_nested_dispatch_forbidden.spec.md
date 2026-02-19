# Governance Cases

## DCGOV-RUNTIME-JOB-DISPATCH-005

```yaml contract-spec
id: DCGOV-RUNTIME-JOB-DISPATCH-005
title: ops.job.dispatch nested dispatch is forbidden
purpose: Ensures runtime emits deterministic failure token when nested dispatch is attempted.
type: contract.check
harness:
  root: .
  ops_job_nested_dispatch:
    path: /dc-runner-rust
    required_tokens:
    - runtime.dispatch.nested_forbidden
  check:
    profile: governance.scan
    config:
      check: runtime.ops_job_nested_dispatch_forbidden
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
