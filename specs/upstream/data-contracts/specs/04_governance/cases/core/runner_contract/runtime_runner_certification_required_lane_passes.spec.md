```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    check:
      profile: governance.scan
      config:
        check: runtime.runner_certification_required_lane_passes
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CERT-004
    title: required rust runner certification lane passes
    purpose: Ensures rust required lane certification passes and remains blocking.
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
