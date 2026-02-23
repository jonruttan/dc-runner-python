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
        check: runtime.harness_jobs_metadata_list_required
contracts:
  clauses:
  - id: DCGOV-RUNTIME-JOB-DISPATCH-002
    title: contract.job harness uses jobs metadata list
    purpose: Ensures contract.job cases declare helper metadata under harness.jobs
      entries.
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
  - id: act.gov.runtime.harness.jobs.met.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.harness.jobs.met.1
  consumes:
  - act.gov.runtime.harness.jobs.met.1
```
