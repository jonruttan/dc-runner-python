# Governance Cases

## DCGOV-RUNTIME-JOB-DISPATCH-002

```yaml contract-spec
id: DCGOV-RUNTIME-JOB-DISPATCH-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: contract.job harness uses jobs metadata map
purpose: Ensures contract.job cases declare helper metadata under harness.jobs entries.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.harness_jobs_metadata_map_required
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
