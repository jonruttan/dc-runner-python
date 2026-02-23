```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
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
contracts:
  clauses:
  - id: DCGOV-RUNTIME-STATUS-002
    title: runner status matrix schema is defined
    purpose: Ensures aggregated status matrix contract shape is declared for governance
      and docs.
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
  - id: act.gov.runtime.runner.status.ma.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.runner.status.ma.1
  consumes:
  - act.gov.runtime.runner.status.ma.1
```

