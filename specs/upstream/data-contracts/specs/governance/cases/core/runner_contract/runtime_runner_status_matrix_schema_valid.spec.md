```yaml contract-spec
id: DCGOV-RUNTIME-STATUS-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner status matrix schema is defined
purpose: Ensures aggregated status matrix contract shape is declared for governance and docs.
type: contract.check
harness:
  root: .
  runner_status_matrix_schema:
    path: /specs/01_schema/runner_status_matrix_v1.yaml
    required_tokens:
    - type: runtime.runner_status_matrix
    - matrix_rows
    - freshness_state
    - policy_effect
  check:
    profile: governance.scan
    config:
      check: runtime.runner_status_matrix_schema_valid
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

