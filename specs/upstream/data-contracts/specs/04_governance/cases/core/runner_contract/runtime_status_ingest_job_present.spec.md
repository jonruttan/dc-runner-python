```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    ci_ingest_job:
      path: /.github/workflows/ci.yml
      required_tokens:
      - runner-status-ingest: null
      - ./scripts/runner_status_ingest.sh --max-age-hours 72 --enforce-freshness
    check:
      profile: governance.scan
      config:
        check: runtime.status_ingest_job_present
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CI-002
    title: status ingest job present in ci
    purpose: Ensures CI includes a status-ingest control-plane job.
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
  - id: act.gov.runtime.status.ingest.jo.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.status.ingest.jo.1
  consumes:
  - act.gov.runtime.status.ingest.jo.1
```
