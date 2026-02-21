```yaml contract-spec
id: DCGOV-RUNTIME-CERT-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: runner certification artifacts follow contract shape
purpose: Ensures runner-certify generates contract-shaped JSON and markdown artifacts.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.runner_certification_artifacts_contract_sync
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
