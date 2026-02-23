```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    check:
      profile: governance.scan
      config:
        check: runtime.contract_job_hooks_refactor_applied
contracts:
  clauses:
  - id: DCGOV-RUNTIME-JOB-HOOKS-001
    title: rust contract.job specs adopt fail and complete lifecycle hooks
    purpose: Ensures Rust job contract-spec cases include when fail and complete dispatches
      with matching hook job metadata.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.contract.job.hoo.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.contract.job.hoo.1
  consumes:
  - act.gov.runtime.contract.job.hoo.1
```
