```yaml contract-spec
id: DCGOV-RUNTIME-JOB-HOOKS-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: rust contract.job specs adopt fail and complete lifecycle hooks
purpose: Ensures Rust job contract-spec cases include when fail and complete dispatches with
  matching hook job metadata.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.contract_job_hooks_refactor_applied
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
