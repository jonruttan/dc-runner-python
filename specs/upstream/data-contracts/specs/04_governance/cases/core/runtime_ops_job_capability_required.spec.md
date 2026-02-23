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
        check: runtime.ops_job_capability_required
contracts:
  clauses:
  - id: DCGOV-RUNTIME-JOB-DISPATCH-004
    title: ops.job.dispatch requires ops.job capability
    purpose: Ensures cases that call ops.job.dispatch declare harness.spec_lang.capabilities
      including ops.job.
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
  - id: act.gov.runtime.ops.job.capabili.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.ops.job.capabili.1
  consumes:
  - act.gov.runtime.ops.job.capabili.1
```
