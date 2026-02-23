```yaml contract-spec
id: DCGOV-PIPE-INGEST-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: status ingest pipeline is chained and contract-verified
purpose: Ensures ingest artifact checks are linked in chain order and validated with status-ingest policy library exports.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.status_ingest_pipeline_chain_valid
  chain:
    fail_fast: true
    steps:
      - id: step_status_report_schema
        class: must
        ref: /specs/governance/cases/core/runner_contract/runtime_runner_status_report_schema_valid.spec.md#DCGOV-RUNTIME-STATUS-001
      - id: step_status_matrix_schema
        class: must
        ref: /specs/governance/cases/core/runner_contract/runtime_runner_status_matrix_schema_valid.spec.md#DCGOV-RUNTIME-STATUS-002
      - id: step_freshness
        class: must
        ref: /specs/governance/cases/core/runner_contract/runtime_compatibility_status_freshness_within_slo.spec.md#DCGOV-RUNTIME-STATUS-004
      - id: step_missing_visibility
        class: must
        ref: /specs/governance/cases/core/runner_contract/runtime_compatibility_missing_status_visibility_required.spec.md#DCGOV-RUNTIME-STATUS-005
  use:
    - ref: /specs/05_libraries/policy/policy_status_ingest.spec.md#LIB-POLICY-INGEST-001
      as: lib_policy_ingest
      symbols:
        - policy.ingest.matrix_has_rows
        - policy.ingest.required_lane_policy_effect_valid
        - policy.ingest.compat_stale_missing_count_within_limit
        - policy.ingest.log_entries_correlate_matrix_rows
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names:
        - violation_count
        - context_json
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
    - id: assert_2
      assert:
        - call:
            - {var: policy.ingest.matrix_has_rows}
            - std.object.get:
                - {var: context_json}
                - runner_status_matrix
        - call:
            - {var: policy.ingest.required_lane_policy_effect_valid}
            - std.object.get:
                - {var: context_json}
                - runner_status_matrix
        - call:
            - {var: policy.ingest.compat_stale_missing_count_within_limit}
            - std.object.get:
                - {var: context_json}
                - runner_status_matrix
        - call:
            - {var: policy.ingest.log_entries_correlate_matrix_rows}
            - lit:
                matrix_rows:
                  - runner_id: dc-runner-rust
                ingest_log:
                  entries:
                    - runner_id: dc-runner-rust
```
