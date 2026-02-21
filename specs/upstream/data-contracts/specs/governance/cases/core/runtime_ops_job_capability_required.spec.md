```yaml contract-spec
id: DCGOV-RUNTIME-JOB-DISPATCH-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops.job.dispatch requires ops.job capability
purpose: Ensures cases that call ops.job.dispatch declare harness.spec_lang.capabilities including
  ops.job.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.ops_job_capability_required
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
