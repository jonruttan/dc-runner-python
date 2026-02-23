```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    profiling_redaction:
      trace_path: specs/04_governance/cases/fixtures/run_trace_sample.json
    check:
      profile: governance.scan
      config:
        check: runtime.profiling_redaction_policy
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
  - id: DCGOV-PROFILE-REDACT-001
    title: run trace redaction policy prevents secret leakage
    purpose: Ensures profiling env metadata does not store raw values and trace payloads
      do not include common secret-like tokens.
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
  - id: act.gov.runtime.profiling.redact.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.profiling.redact.1
  consumes:
  - act.gov.runtime.profiling.redact.1
```

