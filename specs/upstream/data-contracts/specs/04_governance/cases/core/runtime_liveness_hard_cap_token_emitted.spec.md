```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    liveness_trace_tokens:
      trace_path: specs/04_governance/cases/fixtures/run_trace_liveness_sample.json
    check:
      profile: governance.scan
      config:
        check: runtime.liveness_hard_cap_token_emitted
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
  - id: DCGOV-LIVENESS-HARDCAP-001
    title: run trace includes hard-cap and kill escalation reason tokens
    purpose: Ensures emergency hard-cap watchdog behavior is represented in trace
      token taxonomy.
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
  - id: act.gov.runtime.liveness.hard.ca.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.liveness.hard.ca.1
  consumes:
  - act.gov.runtime.liveness.hard.ca.1
```
