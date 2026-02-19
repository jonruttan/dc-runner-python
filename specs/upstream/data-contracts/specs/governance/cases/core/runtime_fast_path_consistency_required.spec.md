# Governance Cases

## DCGOV-RUNTIME-TRIAGE-023

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-023
title: fast-path consistency is enforced across pre-push and gate scripts
type: contract.check
purpose: Ensures fast-path routing tokens remain aligned across local parity, ci gate, and
  managed pre-push hook.
harness:
  root: .
  fast_path_consistency:
    file_token_sets:
    - path: /scripts/local_ci_parity.sh
      required_tokens:
      - paths_all_in_list "specs/governance/check_sets_v1.yaml"
      - is_fast_path_script_only_change
      - paths_all_in_list "scripts/local_ci_parity.sh" "scripts/ci_gate.sh"
      - skip normalize-check (check_sets-only change)
      - skip docs-generate-check (check_sets-only change)
      - skip normalize-check (gate-script-only change)
      - skip docs-generate-check (gate-script-only change)
    - path: /scripts/ci_gate.sh
      required_tokens:
      - SPEC_CI_GATE_LOCAL_FAST_PATH
      - only_check_sets_changes
      - only_gate_script_changes
      - specs/governance/check_sets_v1.yaml
      - CI:-}
      - 'local fast path: check_sets-only change; delegating to local_ci_parity.sh'
      - 'local fast path: gate-script-only change; delegating to local_ci_parity.sh'
    - path: /.githooks/pre-push
      required_tokens:
      - is_check_sets_only_change
      - is_gate_script_only_change
      - specs/governance/check_sets_v1.yaml
      - scripts/local_ci_parity.sh
      - scripts/ci_gate.sh
      - 'fast path: check_sets-only change'
      - 'fast path: gate-script-only change'
      - make prepush
  check:
    profile: governance.scan
    config:
      check: runtime.fast_path_consistency_required
  use:
  - ref: /specs/libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
```
