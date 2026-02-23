```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    runner_status_report_schema:
      path: /specs/01_schema/runner_status_report_v1.yaml
      required_tokens:
      - type: runtime.runner_status_report
      - runner_id
      - implementation_repo
      - generated_at
      - fresh_until
      - command_results
      - artifact_refs
    check:
      profile: governance.scan
      config:
        check: runtime.runner_status_report_schema_valid
contracts:
  clauses:
  - id: DCGOV-RUNTIME-STATUS-001
    title: runner status report schema is defined
    purpose: Ensures runner status exchange producer payload shape is declared and
      stable.
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
  - id: act.gov.runtime.runner.status.re.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.runner.status.re.1
  consumes:
  - act.gov.runtime.runner.status.re.1
```

