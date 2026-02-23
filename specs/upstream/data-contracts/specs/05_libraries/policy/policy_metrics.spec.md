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
    - ref: '#LIB-POLICY-002-001-POLICY-METRIC-NON-DECREASE'
      as: lib_non_decrease
      symbols:
      - policy.metric_non_decrease
    - ref: '#LIB-POLICY-002-002-POLICY-METRIC-NON-INCREASE'
      as: lib_non_increase
      symbols:
      - policy.metric_non_increase
    exports:
    - as: policy.metric_non_increase
      from: assert.function
      path: /__export__policy.metric_non_increase
      params:
      - subject
      - field
      - baseline_field
      - epsilon
      required: true
      docs:
      - id: policy.metric_non_increase.doc.1
        summary: Contract export for `policy.metric_non_increase`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  field: \"<field>\"\n\
          \  baseline_field: \"<baseline_field>\"\n  epsilon: \"<epsilon>\"\nexpected:\
          \ \"<result>\"\nnotes: Replace with a concrete scenario.\n- params: - name:\
          \ subject\n  type: any\n  required: true\n  description: Input parameter\
          \ `subject`.\n- name: field\n  type: any\n  required: true\n  description:\
          \ Input parameter `field`.\n- name: baseline_field\n  type: any\n  required:\
          \ true\n  description: Input parameter `baseline_field`.\n- name: epsilon\n\
          \  type: any\n  required: true\n  description: Input parameter `epsilon`.\n\
          - returns: type: any\ndescription: Result payload for this symbol.\\ n-\
          \ errors: - code: SCHEMA_ERROR\n  when: Input payload does not satisfy contract\
          \ shape requirements.\n  category: schema\n- portability: python: true\n\
          php: true\nrust: true\nnotes: Confirm per-runtime behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-POLICY-002-001-POLICY-METRIC-NON-DECREASE
    title: 'policy-metrics reusable non-regression predicates: policy.metric_non_decrease'
    docs:
    - summary: Case `LIB-POLICY-002-001-POLICY-METRIC-NON-DECREASE` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: policy.policy.metrics
      module: policy
      stability: alpha
      owner: data-contracts
      tags:
      - policy
    type: contract.export
    asserts:
      checks:
      - id: __export__policy.metric_non_decrease
        assert:
          std.logic.gte:
          - std.math.add:
            - std.object.get:
              - var: subject
              - var: field
            - var: epsilon
          - std.object.get:
            - var: subject
            - var: baseline_field
  - id: LIB-POLICY-002-002-POLICY-METRIC-NON-INCREASE
    title: 'policy-metrics reusable non-regression predicates: policy.metric_non_increase'
    docs:
    - summary: Case `LIB-POLICY-002-002-POLICY-METRIC-NON-INCREASE` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: policy.policy.metrics
      module: policy
      stability: alpha
      owner: data-contracts
      tags:
      - policy
    type: contract.export
    asserts:
      checks:
      - id: __export__policy.metric_non_increase
        assert:
          std.logic.lte:
          - std.math.sub:
            - std.object.get:
              - var: subject
              - var: field
            - var: epsilon
          - std.object.get:
            - var: subject
            - var: baseline_field
  - id: LIB-POLICY-002-900-POLICY-METRIC-SMOKE
    title: policy metric helpers execute as colocated executable checks
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
          - var: policy.metric_non_decrease
          - lit:
              current: 10
              baseline: 9
          - current
          - baseline
          - 0
        - call:
          - var: policy.metric_non_increase
          - lit:
              current: 8
              baseline: 9
          - current
          - baseline
          - 0
adapters:
- type: beta.exports_as_policy_metric_non_decrease_from_assert_function_path_export_policy_metric_non_decrease_params_subject_field_baseline_field_epsilon_required_true_docs_id_policy_metric_non_decrease_doc_1_summary_contract_export_for_policy_metric_non_decrease_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_field_field_n_baseline_field_baseline_field_n_epsilon_epsilon_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_field_n_type_any_n_required_true_n_description_input_parameter_field_n_name_baseline_field_n_type_any_n_required_true_n_description_input_parameter_baseline_field_n_name_epsilon_n_type_any_n_required_true_n_description_input_parameter_epsilon_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.policy.metrics.spec.1
    profile: default
- type: beta.exports_as_policy_metric_non_increase_from_assert_function_path_export_policy_metric_non_increase_params_subject_field_baseline_field_epsilon_required_true_docs_id_policy_metric_non_increase_doc_1_summary_contract_export_for_policy_metric_non_increase_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_field_field_n_baseline_field_baseline_field_n_epsilon_epsilon_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_field_n_type_any_n_required_true_n_description_input_parameter_field_n_name_baseline_field_n_type_any_n_required_true_n_description_input_parameter_baseline_field_n_name_epsilon_n_type_any_n_required_true_n_description_input_parameter_epsilon_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.policy.metrics.spec.2
    profile: default
- type: beta.check_profile_text_file_config_use_ref_lib_policy_002_001_policy_metric_non_decrease_as_lib_non_decrease_symbols_policy_metric_non_decrease_ref_lib_policy_002_002_policy_metric_non_increase_as_lib_non_increase_symbols_policy_metric_non_increase
  actions:
  - id: act.lib.policy.metrics.spec.3
    profile: default
services:
- id: svc.lib.policy.metrics.spec.1
  consumes:
  - act.lib.policy.metrics.spec.1
- id: svc.lib.policy.metrics.spec.2
  consumes:
  - act.lib.policy.metrics.spec.2
- id: svc.lib.policy.metrics.spec.3
  consumes:
  - act.lib.policy.metrics.spec.3
```


