```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    compatibility_lanes:
      workflow: /.github/workflows/ci.yml
      required_tokens:
      - compatibility-python-lane: null
      - compatibility-php-lane: null
      - compatibility-node-lane: null
      - compatibility-c-lane: null
      - continue-on-error: true
    check:
      profile: governance.scan
      config:
        check: runtime.compatibility_lanes_non_blocking_status
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
  - id: DCGOV-RUNTIME-CONFIG-007
    title: compatibility lanes remain non-blocking
    purpose: Ensures compatibility runtime lanes are present in CI and explicitly
      non-blocking.
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
  - id: act.gov.runtime.compatibility.la.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.compatibility.la.1
  consumes:
  - act.gov.runtime.compatibility.la.1
```
