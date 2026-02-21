```yaml contract-spec
id: DCGOV-RUNTIME-CI-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: status ingest job present in ci
purpose: Ensures CI includes a status-ingest control-plane job.
type: contract.check
harness:
  root: .
  ci_ingest_job:
    path: /.github/workflows/ci.yml
    required_tokens:
    - runner-status-ingest:
    - ./scripts/runner_status_ingest.sh --max-age-hours 72 --enforce-freshness
  check:
    profile: governance.scan
    config:
      check: runtime.status_ingest_job_present
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
