```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    triage_targeted_first:
      path: /scripts/governance_triage.sh
      required_tokens:
      - TRIAGE_MODE_DEFAULT
      - targeted-first
      - broad-first
      - resolve_targeted_prefixes
      - selection_source
    check:
      profile: governance.scan
      config:
        check: runtime.governance_triage_targeted_first_required
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
  - id: DCGOV-RUNTIME-TRIAGE-008
    title: governance triage auto mode is targeted-first by default
    purpose: Ensures triage auto mode resolves to targeted-first and exposes broad-first
      as an explicit mode.
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
  - id: act.gov.runtime.governance.triag.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.governance.triag.1
  consumes:
  - act.gov.runtime.governance.triag.1
```
