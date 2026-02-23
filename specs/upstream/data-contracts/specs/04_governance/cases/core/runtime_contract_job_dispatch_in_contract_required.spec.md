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
        check: runtime.contract_job_dispatch_in_contract_required
contracts:
  clauses:
  - id: DCGOV-RUNTIME-JOB-DISPATCH-001
    title: contract.job dispatch must be declared in contract
    purpose: Ensures contract.job cases dispatch jobs via ops.job.dispatch in contract
      assertions.
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
  - id: act.gov.runtime.contract.job.dis.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.contract.job.dis.1
  consumes:
  - act.gov.runtime.contract.job.dis.1
```
