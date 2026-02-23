```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    ci_workflow_critical_gate:
      path: /.github/workflows/ci.yml
      required_tokens:
      - 'control-plane-critical-gate:'
      - Run control-plane critical gate
      - ./scripts/control_plane.sh critical-gate
      - 'needs: control-plane-critical-gate'
      - 'continue-on-error: true'
    check:
      profile: governance.scan
      config:
        check: runtime.ci_workflow_critical_gate_required
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
  - id: DCGOV-RUNTIME-TRIAGE-014
    title: ci workflow defines rust critical gate as first-class lane
    purpose: Ensures CI has a dedicated rust critical gate job and diagnostic ci-gate
      depends on it.
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
  - id: act.gov.runtime.ci.workflow.crit.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.ci.workflow.crit.1
  consumes:
  - act.gov.runtime.ci.workflow.crit.1
```
