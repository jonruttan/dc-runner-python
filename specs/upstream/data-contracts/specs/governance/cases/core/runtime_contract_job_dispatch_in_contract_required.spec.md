```yaml contract-spec
id: DCGOV-RUNTIME-JOB-DISPATCH-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: contract.job dispatch must be declared in contract
purpose: Ensures contract.job cases dispatch jobs via ops.job.dispatch in contract assertions.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.contract_job_dispatch_in_contract_required
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
