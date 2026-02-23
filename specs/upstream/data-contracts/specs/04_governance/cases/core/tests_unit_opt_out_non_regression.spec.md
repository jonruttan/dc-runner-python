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
        check: tests.unit_opt_out_non_regression
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
  - id: DCGOV-TEST-UNIT-OPT-OUT-001
    title: unit test opt-out usage is measured and non-regressing
    purpose: Tracks unit-test opt-out usage and enforces a non-regression baseline
      so opt-out coverage is reduced over time.
    asserts:
      imports:
      - from: asset
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - tests.unit_opt_out_non_regression
adapters:
- type: beta.scan
  actions:
  - id: act.gov.tests.unit.opt.out.non.r.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.tests.unit.opt.out.non.r.1
  consumes:
  - act.gov.tests.unit.opt.out.non.r.1
```
