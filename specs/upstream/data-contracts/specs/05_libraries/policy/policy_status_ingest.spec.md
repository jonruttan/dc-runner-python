```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    check:
      profile: text.file
      config: {}
    use:
    - ref: '#LIB-POLICY-INGEST-001'
      as: lib_policy_ingest
      symbols:
      - policy.ingest.matrix_has_rows
      - policy.ingest.required_lane_policy_effect_valid
      - policy.ingest.compat_stale_missing_count_within_limit
      - policy.ingest.log_entries_correlate_matrix_rows
    exports:
    - as: policy.ingest.matrix_has_rows
      from: assert.function
      path: /__export__policy.ingest.matrix_has_rows
      params:
      - subject
      required: true
    - as: policy.ingest.required_lane_policy_effect_valid
      from: assert.function
      path: /__export__policy.ingest.required_lane_policy_effect_valid
      params:
      - subject
      required: true
    - as: policy.ingest.compat_stale_missing_count_within_limit
      from: assert.function
      path: /__export__policy.ingest.compat_stale_missing_count_within_limit
      params:
      - subject
      required: true
    - as: policy.ingest.log_entries_correlate_matrix_rows
      from: assert.function
      path: /__export__policy.ingest.log_entries_correlate_matrix_rows
      params:
      - subject
      required: true
contracts:
  clauses:
  - id: LIB-POLICY-INGEST-001
    title: status ingest predicates
    library:
      id: policy.status.ingest
      module: policy
      stability: alpha
      owner: data-contracts
      tags:
      - policy
      - runtime
    type: contract.export
    asserts:
      checks:
      - id: __export__policy.ingest.matrix_has_rows
        assert:
          std.logic.gt:
          - std.collection.length:
            - std.object.get:
              - var: subject
              - matrix_rows
          - 0
      - id: __export__policy.ingest.required_lane_policy_effect_valid
        assert:
          std.logic.not:
          - std.collection.any:
            - std.object.get:
              - var: subject
              - matrix_rows
            - std.logic.and:
              - std.logic.eq:
                - std.object.get:
                  - var: item
                  - lane_class
                - required
              - std.logic.not:
                - std.logic.eq:
                  - std.object.get:
                    - var: item
                    - policy_effect
                  - blocking_fail
      - id: __export__policy.ingest.compat_stale_missing_count_within_limit
        assert:
          std.logic.gte:
          - 0
          - 0
      - id: __export__policy.ingest.log_entries_correlate_matrix_rows
        assert:
          std.logic.eq:
          - std.collection.length:
            - std.object.get:
              - var: subject
              - matrix_rows
          - std.collection.length:
            - std.object.get:
              - std.object.get:
                - var: subject
                - ingest_log
              - entries
  - id: LIB-POLICY-INGEST-900
    title: status ingest policy library smoke
    type: contract.check
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.ingest.matrix_has_rows
          - lit:
              matrix_rows:
              - runner_id: dc-runner-rust
              ingest_log:
                entries:
                - runner_id: dc-runner-rust
        - call:
          - var: policy.ingest.required_lane_policy_effect_valid
          - lit:
              matrix_rows:
              - lane_class: required
                policy_effect: blocking_fail
        - call:
          - var: policy.ingest.compat_stale_missing_count_within_limit
          - lit: {}
        - call:
          - var: policy.ingest.log_entries_correlate_matrix_rows
          - lit:
              matrix_rows:
              - runner_id: dc-runner-rust
              ingest_log:
                entries:
                - runner_id: dc-runner-rust
adapters:
- type: beta.exports_as_policy_ingest_matrix_has_rows_from_assert_function_path_export_policy_ingest_matrix_has_rows_params_subject_required_true_as_policy_ingest_required_lane_policy_effect_valid_from_assert_function_path_export_policy_ingest_required_lane_policy_effect_valid_params_subject_required_true_as_policy_ingest_compat_stale_missing_count_within_limit_from_assert_function_path_export_policy_ingest_compat_stale_missing_count_within_limit_params_subject_required_true_as_policy_ingest_log_entries_correlate_matrix_rows_from_assert_function_path_export_policy_ingest_log_entries_correlate_matrix_rows_params_subject_required_true
  actions:
  - id: act.lib.policy.status.ingest.spe.1
    profile: default
- type: beta.check_profile_text_file_config_use_ref_lib_policy_ingest_001_as_lib_policy_ingest_symbols_policy_ingest_matrix_has_rows_policy_ingest_required_lane_policy_effect_valid_policy_ingest_compat_stale_missing_count_within_limit_policy_ingest_log_entries_correlate_matrix_rows
  actions:
  - id: act.lib.policy.status.ingest.spe.2
    profile: default
services:
- id: svc.lib.policy.status.ingest.spe.1
  consumes:
  - act.lib.policy.status.ingest.spe.1
- id: svc.lib.policy.status.ingest.spe.2
  consumes:
  - act.lib.policy.status.ingest.spe.2
```


