```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    readme_usage_paths:
      path: /README.md
      required_tokens:
      - How Users Use This Project
      - Author a spec change
      - Validate docs and contract coherence
      - Read compatibility and status telemetry
      - Debug governance or documentation drift
    check:
      profile: governance.scan
      config:
        check: docs.readme_task_usage_paths_present
contracts:
  clauses:
  - id: DCGOV-DOCS-REF-025
    title: readme includes task-based usage paths
    purpose: Ensures README is user-oriented and includes concrete task navigation.
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
  - id: act.gov.docs.readme.task.usage.p.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.readme.task.usage.p.1
  consumes:
  - act.gov.docs.readme.task.usage.p.1
```
