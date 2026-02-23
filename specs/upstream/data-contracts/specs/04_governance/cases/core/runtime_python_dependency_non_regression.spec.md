```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    python_dependency_non_regression:
      baseline_path: /specs/04_governance/metrics/python_dependency_baseline.json
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
    - ref: /specs/05_libraries/policy/policy_assertions.spec.md
      as: lib_policy_core_spec
      symbols:
      - policy.assert.no_violations
      - policy.assert.summary_passed
      - policy.assert.summary_check_id
      - policy.assert.scan_pass
contracts:
  clauses:
  - id: DCGOV-RUNTIME-PYDEP-002
    title: python dependency metric is non-regressing
    purpose: Enforces monotonic non-regression for python dependency metrics against
      checked-in baseline.
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
      - id: assert_2
        assert:
        - call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
        - call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - runtime.compatibility_python_lane_dependency_non_regression
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.python.dependenc.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.python.dependenc.1
  consumes:
  - act.gov.runtime.python.dependenc.1
```
