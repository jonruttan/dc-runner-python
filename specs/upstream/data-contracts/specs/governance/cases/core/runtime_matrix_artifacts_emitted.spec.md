# Governance Cases

## DCGOV-RUNTIME-CI-003

```yaml contract-spec
id: DCGOV-RUNTIME-CI-003
title: matrix artifacts are emitted in ci
purpose: Ensures CI publishes canonical status matrix artifacts.
type: contract.check
harness:
  root: .
  ci_matrix_artifacts:
    path: /.github/workflows/ci.yml
    required_tokens:
    - .artifacts/runner-status-matrix.json
    - .artifacts/runner-status-matrix.md
    - .artifacts/runner-status-ingest-log.json
  check:
    profile: governance.scan
    config:
      check: runtime.matrix_artifacts_emitted
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
