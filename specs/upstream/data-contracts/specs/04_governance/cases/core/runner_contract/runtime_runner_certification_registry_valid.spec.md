```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    runner_certification:
      path: /specs/01_schema/runner_certification_registry_v1.yaml
      required_runner_ids:
      - rust
      - python
      - php
      - node
      - c
    check:
      profile: governance.scan
      config:
        check: runtime.runner_certification_registry_valid
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CERT-001
    title: runner certification registry shape is valid
    purpose: Ensures runner certification registry entries are complete and deterministic.
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
  - id: act.gov.runtime.runner.certifica.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.runner.certifica.1
  consumes:
  - act.gov.runtime.runner.certifica.1
```
