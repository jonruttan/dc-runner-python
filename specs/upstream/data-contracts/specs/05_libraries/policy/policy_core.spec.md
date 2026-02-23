```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: policy.pass_when_no_violations
      from: assert.function
      path: /__export__policy.pass_when_no_violations
      params:
      - subject
      required: true
      docs:
      - id: policy.pass_when_no_violations.doc.1
        summary: Contract export for `policy.pass_when_no_violations`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\nexpected: \"<result>\"\n\
          notes: Replace with a concrete scenario.\n- params: - name: subject\n  type:\
          \ any\n  required: true\n  description: Input parameter `subject`.\\ n-\
          \ returns: type: any\ndescription: Result payload for this symbol.\n- errors:\
          \ - code: SCHEMA_ERROR\n  when: Input payload does not satisfy contract\
          \ shape requirements.\n  category: schema\n- portability: python: true\n\
          php: true\\ nrust: true\nnotes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: policy.fail_when_has_violations
      from: assert.function
      path: /__export__policy.fail_when_has_violations
      params:
      - subject
      required: true
      docs:
      - id: policy.fail_when_has_violations.doc.1
        summary: Contract export for `policy.fail_when_has_violations`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\nexpected: \"<result>\"\n\
          notes: Replace with a concrete scenario.\n- params: - name: subject\n  type:\
          \ any\n  required: true\n  description: Input parameter `subject`.\\ n-\
          \ returns: type: any\ndescription: Result payload for this symbol.\n- errors:\
          \ - code: SCHEMA_ERROR\n  when: Input payload does not satisfy contract\
          \ shape requirements.\n  category: schema\n- portability: python: true\n\
          php: true\\ nrust: true\nnotes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: policy.check_id_is
      from: assert.function
      path: /__export__policy.check_id_is
      params:
      - subject
      - expected
      required: true
      docs:
      - id: policy.check_id_is.doc.1
        summary: Contract export for `policy.check_id_is`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  expected: \"<expected>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\\ n-\
          \ params: - name: subject\n  type: any\n  required: true\n  description:\
          \ Input parameter `subject`.\n- name: expected\n  type: any\n  required:\
          \ true\n  description: Input parameter `expected`.\n- returns: type: any\n\
          description: Result payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n\
          \  when: Input payload does not satisfy contract shape requirements.\n \
          \ category: schema\\ n- portability: python: true\nphp: true\nrust: true\n\
          notes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: policy.violation_count_is
      from: assert.function
      path: /__export__policy.violation_count_is
      params:
      - subject
      - expected
      required: true
      docs:
      - id: policy.violation_count_is.doc.1
        summary: Contract export for `policy.violation_count_is`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  expected: \"<expected>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\\ n-\
          \ params: - name: subject\n  type: any\n  required: true\n  description:\
          \ Input parameter `subject`.\n- name: expected\n  type: any\n  required:\
          \ true\n  description: Input parameter `expected`.\n- returns: type: any\n\
          description: Result payload for this symbol.\\ n- errors: - code: SCHEMA_ERROR\n\
          \  when: Input payload does not satisfy contract shape requirements.\n \
          \ category: schema\\ n- portability: python: true\nphp: true\nrust: true\n\
          notes: Confirm per-runtime behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-POLICY-001
    title: policy-core reusable governance predicates
    docs:
    - summary: Case `LIB-POLICY-001` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: policy.policy.core
      module: policy
      stability: alpha
      owner: data-contracts
      tags:
      - policy
    asserts:
      checks:
      - id: __export__policy.pass_when_no_violations
        assert:
          std.collection.is_empty:
          - std.object.get:
            - var: subject
            - violations
      - id: __export__policy.fail_when_has_violations
        assert:
          std.logic.not:
          - call:
            - var: policy.pass_when_no_violations
            - var: subject
      - id: __export__policy.check_id_is
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - check_id
          - var: expected
      - id: __export__policy.violation_count_is
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - violation_count
          - var: expected
adapters:
- type: beta.exports_as_policy_pass_when_no_violations_from_assert_function_path_export_policy_pass_when_no_violations_params_subject_required_true_docs_id_policy_pass_when_no_violations_doc_1_summary_contract_export_for_policy_pass_when_no_violations_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_policy_fail_when_has_violations_from_assert_function_path_export_policy_fail_when_has_violations_params_subject_required_true_docs_id_policy_fail_when_has_violations_doc_1_summary_contract_export_for_policy_fail_when_has_violations_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_policy_check_id_is_from_assert_function_path_export_policy_check_id_is_params_subject_expected_required_true_docs_id_policy_check_id_is_doc_1_summary_contract_export_for_policy_check_id_is_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_expected_expected_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_expected_n_type_any_n_required_true_n_description_input_parameter_expected_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_policy_violation_count_is_from_assert_function_path_export_policy_violation_count_is_params_subject_expected_required_true_docs_id_policy_violation_count_is_doc_1_summary_contract_export_for_policy_violation_count_is_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_expected_expected_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_expected_n_type_any_n_required_true_n_description_input_parameter_expected_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.policy.core.spec.1
    direction: bidirectional
    profile: default
services:
- id: svc.lib.policy.core.spec.1
  consumes:
  - act.lib.policy.core.spec.1
```
