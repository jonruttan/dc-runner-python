# Governance Cases

## DCGOV-RUNTIME-PYDEP-002

```yaml contract-spec
id: DCGOV-RUNTIME-PYDEP-002
title: python dependency metric is non-regressing
purpose: Enforces monotonic non-regression for python dependency metrics against checked-in
  baseline.
type: contract.check
harness:
  root: .
  python_dependency_non_regression:
    baseline_path: /specs/governance/metrics/python_dependency_baseline.json
    summary_fields:
      non_python_lane_python_exec_count: non_increase
      transitive_adapter_python_exec_count: non_increase
      python_usage_scope_violation_count: non_increase
      default_lane_python_free_ratio: non_decrease
    segment_fields: {}
    epsilon: 1.0e-12
    python_dependency: {}
  check:
    profile: governance.scan
    config:
      check: runtime.compatibility_python_lane_dependency_non_regression
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
      - runtime.compatibility_python_lane_dependency_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
