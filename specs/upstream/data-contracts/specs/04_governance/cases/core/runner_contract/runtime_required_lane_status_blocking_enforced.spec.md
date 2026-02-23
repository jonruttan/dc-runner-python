```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    required_lane_policy:
      path: /scripts/runner_status_ingest.sh
      required_tokens:
      - lane_class
      - required
      - blocking_fail
    check:
      profile: governance.scan
      config:
        check: runtime.required_lane_status_blocking_enforced
contracts:
  clauses:
  - id: DCGOV-RUNTIME-STATUS-006
    title: required lane status remains blocking
    purpose: Ensures required-lane status outcomes map to blocking policy effects.
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
  - id: act.gov.runtime.required.lane.st.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.required.lane.st.1
  consumes:
  - act.gov.runtime.required.lane.st.1
```

