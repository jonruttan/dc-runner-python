```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    ci_python_lane_non_blocking:
      workflow: /.github/workflows/ci.yml
      required_tokens:
      - compatibility-python-lane: null
      - continue-on-error: true
      - Run Python compatibility lane (non-blocking)
      forbidden_tokens:
      - python-parity-lane: null
    check:
      profile: governance.scan
      config:
        check: runtime.ci_python_lane_non_blocking_required
    use:
    - ref: /specs/05_libraries/policy/policy_assertions.spec.md
      as: lib_policy_core_spec
      symbols:
      - policy.assert.no_violations
      - policy.assert.summary_passed
      - policy.assert.summary_check_id
      - policy.assert.scan_pass
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CONFIG-005
    title: python compatibility lane remains non-blocking
    purpose: Ensures Python compatibility lane exists in CI and is configured as non-blocking.
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
  - id: act.gov.runtime.ci.python.lane.n.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.ci.python.lane.n.1
  consumes:
  - act.gov.runtime.ci.python.lane.n.1
```
