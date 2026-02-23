```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
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
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CI-003
    title: matrix artifacts are emitted in ci
    purpose: Ensures CI publishes canonical status matrix artifacts.
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
  - id: act.gov.runtime.matrix.artifacts.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.matrix.artifacts.1
  consumes:
  - act.gov.runtime.matrix.artifacts.1
```
