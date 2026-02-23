```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    fast_path_consistency:
      file_token_sets:
      - path: /scripts/ci_gate.sh
        required_tokens:
        - paths_all_in_list "specs/04_governance/check_sets_v1.yaml"
        - is_fast_path_script_only_change
        - paths_all_in_list "scripts/ci_gate.sh" "scripts/ci_gate.sh"
        - skip normalize-check (check_sets-only change)
        - skip docs-generate-check (check_sets-only change)
        - skip normalize-check (gate-script-only change)
        - skip docs-generate-check (gate-script-only change)
      - path: /scripts/ci_gate.sh
        required_tokens:
        - SPEC_CI_GATE_LOCAL_FAST_PATH
        - only_check_sets_changes
        - only_gate_script_changes
        - specs/04_governance/check_sets_v1.yaml
        - CI:-}
        - 'local fast path: check_sets-only change; delegating to ci_gate.sh'
        - 'local fast path: gate-script-only change; delegating to ci_gate.sh'
      - path: /.githooks/pre-push
        required_tokens:
        - is_check_sets_only_change
        - is_gate_script_only_change
        - specs/04_governance/check_sets_v1.yaml
        - scripts/ci_gate.sh
        - scripts/ci_gate.sh
        - 'fast path: check_sets-only change'
        - 'fast path: gate-script-only change'
        - make prepush
    check:
      profile: governance.scan
      config:
        check: runtime.fast_path_consistency_required
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
  - id: DCGOV-RUNTIME-TRIAGE-023
    title: fast-path consistency is enforced across pre-push and gate scripts
    purpose: Ensures fast-path routing tokens remain aligned across local parity,
      ci gate, and managed pre-push hook.
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
  - id: act.gov.runtime.fast.path.consis.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.fast.path.consis.1
  consumes:
  - act.gov.runtime.fast.path.consis.1
```
