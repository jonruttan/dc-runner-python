```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    triage_bypass_logging:
      path: /.githooks/pre-push
      required_tokens:
      - SPEC_PREPUSH_BYPASS
      - 'WARNING: bypass enabled'
    check:
      profile: governance.scan
      config:
        check: runtime.triage_bypass_logged_required
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
  - id: DCGOV-RUNTIME-TRIAGE-006
    title: emergency bypass remains explicit and logged
    purpose: Ensures pre-push bypass remains explicit and emits deterministic warning
      output.
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
  - id: act.gov.runtime.triage.bypass.lo.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.triage.bypass.lo.1
  consumes:
  - act.gov.runtime.triage.bypass.lo.1
```
