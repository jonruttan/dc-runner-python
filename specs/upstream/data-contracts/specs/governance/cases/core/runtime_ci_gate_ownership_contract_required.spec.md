# Governance Cases

## DCGOV-RUNTIME-TRIAGE-019

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-019
title: ci gate ownership contract is single-source and broad-only in summary
purpose: Ensures ci_gate.sh owns critical execution ordering and ci-gate-summary owns broad
  governance only.
type: contract.check
harness:
  root: .
  ci_gate_ownership_contract:
    gate_path: /scripts/ci_gate.sh
    gate_required_tokens:
    - critical-gate
    - ci-gate-summary
    gate_ordered_tokens:
    - critical-gate
    - ci-gate-summary
    summary_files:
    - /dc-runner-python
    - /dc-runner-rust
    summary_required_tokens:
    - governance_broad
    - triage_phase
    - broad_required
    summary_forbidden_tokens:
    - governance_critical
    - SPEC_CI_GATE_INCLUDE_CRITICAL
    - SPEC_CI_GATE_SKIP_CRITICAL
    - --include-critical
  check:
    profile: governance.scan
    config:
      check: runtime.ci_gate_ownership_contract_required
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
