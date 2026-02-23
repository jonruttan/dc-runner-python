```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    prepush_governance_triage:
      path: /scripts/ci_gate.sh
      required_tokens:
      - governance-triage
      - ./scripts/governance_triage.sh
      forbidden_tokens:
      - run_step governance "${SPEC_RUNNER_BIN}" governance
    check:
      profile: governance.scan
      config:
        check: runtime.prepush_uses_governance_triage_required
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
  - id: DCGOV-RUNTIME-TRIAGE-002
    title: prepush lane uses governance triage entrypoint
    purpose: Ensures prepush parity lane calls governance triage instead of direct
      broad governance.
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
  - id: act.gov.runtime.prepush.uses.gov.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.prepush.uses.gov.1
  consumes:
  - act.gov.runtime.prepush.uses.gov.1
```
