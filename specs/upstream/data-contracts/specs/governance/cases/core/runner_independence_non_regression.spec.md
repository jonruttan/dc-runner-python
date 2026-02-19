# Governance Cases

## DCGOV-RUNTIME-INDEP-002

```yaml contract-spec
id: DCGOV-RUNTIME-INDEP-002
title: runner independence metric is non-regressing
purpose: Enforces monotonic non-regression for runner independence metrics against checked-in
  baseline.
type: contract.check
harness:
  root: .
  runner_independence_non_regression:
    baseline_path: /specs/governance/metrics/runner_independence_baseline.json
    summary_fields:
      overall_runner_independence_ratio: non_decrease
      direct_runtime_invocation_count: non_increase
    segment_fields:
      gate_scripts:
        mean_runner_interface_usage_ratio: non_decrease
    epsilon: 1.0e-12
    runner_independence:
      segment_files:
        gate_scripts:
        - scripts/ci_gate.sh
        - scripts/core_gate.sh
        - scripts/docs_doctor.sh
        ci_workflows:
        - .github/workflows/*.yml
        adapter_interfaces:
        - runners/public/runner_adapter.sh
        - dc-runner-rust
        - dc-runner-rust
      direct_runtime_token_segments:
      - gate_scripts
      - ci_workflows
  check:
    profile: governance.scan
    config:
      check: runtime.runner_independence_non_regression
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
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - runtime.runner_independence_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
