# Governance Cases

## DCGOV-RUNTIME-TRIAGE-014

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-014
title: ci workflow defines rust critical gate as first-class lane
purpose: Ensures CI has a dedicated rust critical gate job and diagnostic ci-gate depends
  on it.
type: contract.check
harness:
  root: .
  ci_workflow_critical_gate:
    path: /.github/workflows/ci.yml
    required_tokens:
    - 'rust-critical-gate:'
    - Run rust critical gate
    - ./runners/public/runner_adapter.sh --impl rust critical-gate
    - 'needs: rust-critical-gate'
    - 'continue-on-error: true'
  check:
    profile: governance.scan
    config:
      check: runtime.ci_workflow_critical_gate_required
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
