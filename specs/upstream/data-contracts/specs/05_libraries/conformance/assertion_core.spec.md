```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: conf.pass_when_text_contains
      from: assert.function
      path: /__export__conf.pass_when_text_contains
      params:
      - subject
      - token
      required: true
      docs:
      - id: conf.pass_when_text_contains.doc.1
        summary: Contract export for `conf.pass_when_text_contains`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  token: \"<token>\"\n\
          expected: \"<result>\"\nnotes: Replace with a concrete scenario.\\ n- params:\
          \ - name: subject\n  type: any\n  required: true\n  description: Input parameter\
          \ `subject`.\n- name: token\n  type: any\n  required: true\n  description:\
          \ Input parameter `token`.\n- returns: type: any\ndescription: Result payload\
          \ for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input payload\
          \ does not satisfy contract shape requirements.\n  category: schema\\ n-\
          \ portability: python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime\
          \ behavior and caveats."
        since: v1
    - as: conf.pass_when_text_regex
      from: assert.function
      path: /__export__conf.pass_when_text_regex
      params:
      - subject
      - pattern
      required: true
      docs:
      - id: conf.pass_when_text_regex.doc.1
        summary: Contract export for `conf.pass_when_text_regex`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  pattern: \"<pattern>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\\ n-\
          \ params: - name: subject\n  type: any\n  required: true\n  description:\
          \ Input parameter `subject`.\n- name: pattern\n  type: any\n  required:\
          \ true\n  description: Input parameter `pattern`.\n- returns: type: any\n\
          description: Result payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n\
          \  when: Input payload does not satisfy contract shape requirements.\n \
          \ category: schema\\ n- portability: python: true\nphp: true\nrust: true\n\
          notes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: conf.eq
      from: assert.function
      path: /__export__conf.eq
      params:
      - subject
      - value
      required: true
      docs:
      - id: conf.eq.doc.1
        summary: Contract export for `conf.eq`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  value: \"<value>\"\n\
          expected: \"<result>\"\nnotes: Replace with a concrete scenario.\n- params:\
          \ - name: subject\n  type: any\n  required: true\n  description: Input parameter\
          \ `subject`.\n- name: value\n  type: any\n  required: true\n  description:\
          \ Input parameter `value`.\n- returns: type: any\ndescription: Result payload\
          \ for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input payload\
          \ does not satisfy contract shape requirements.\n  category: schema\n- portability:\
          \ python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime behavior\
          \ and caveats."
        since: v1
    - as: conf.has_error_category
      from: assert.function
      path: /__export__conf.has_error_category
      params:
      - subject
      - category
      required: true
      docs:
      - id: conf.has_error_category.doc.1
        summary: Contract export for `conf.has_error_category`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  category: \"<category>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\\ n-\
          \ params: - name: subject\n  type: any\n  required: true\n  description:\
          \ Input parameter `subject`.\n- name: category\n  type: any\n  required:\
          \ true\n  description: Input parameter `category`.\n- returns: type: any\n\
          description: Result payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n\
          \  when: Input payload does not satisfy contract shape requirements.\n \
          \ category: schema\\ n- portability: python: true\nphp: true\nrust: true\n\
          notes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: conf.json_type_is
      from: assert.function
      path: /__export__conf.json_type_is
      params:
      - subject
      - type_name
      required: true
      docs:
      - id: conf.json_type_is.doc.1
        summary: Contract export for `conf.json_type_is`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  type_name: \"<type_name>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\n- params:\
          \ - name: subject\n  type: any\n  required: true\n  description: Input parameter\
          \ `subject`.\n- name: type_name\n  type: any\n  required: true\n  description:\
          \ Input parameter `type_name`.\n- returns: type: any\ndescription: Result\
          \ payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input\
          \ payload does not satisfy contract shape requirements.\n  category: schema\n\
          - portability: python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime\
          \ behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-CONF-ASSERT-001
    title: reusable conformance assertion helper functions
    docs:
    - summary: Case `LIB-CONF-ASSERT-001` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: conformance.assertion.core
      module: conformance
      stability: alpha
      owner: data-contracts
      tags:
      - conformance
    asserts:
      checks:
      - id: __export__conf.pass_when_text_contains
        assert:
          std.string.contains:
          - var: subject
          - var: token
      - id: __export__conf.pass_when_text_regex
        assert:
          std.string.regex_match:
          - var: subject
          - var: pattern
      - id: __export__conf.eq
        assert:
          std.logic.eq:
          - var: subject
          - var: value
      - id: __export__conf.has_error_category
        assert:
          std.string.contains:
          - var: subject
          - var: category
      - id: __export__conf.json_type_is
        assert:
          std.type.json_type:
          - var: subject
          - var: type_name
adapters:
- type: beta.exports_as_conf_pass_when_text_contains_from_assert_function_path_export_conf_pass_when_text_contains_params_subject_token_required_true_docs_id_conf_pass_when_text_contains_doc_1_summary_contract_export_for_conf_pass_when_text_contains_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_token_token_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_token_n_type_any_n_required_true_n_description_input_parameter_token_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_conf_pass_when_text_regex_from_assert_function_path_export_conf_pass_when_text_regex_params_subject_pattern_required_true_docs_id_conf_pass_when_text_regex_doc_1_summary_contract_export_for_conf_pass_when_text_regex_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_pattern_pattern_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_pattern_n_type_any_n_required_true_n_description_input_parameter_pattern_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_conf_eq_from_assert_function_path_export_conf_eq_params_subject_value_required_true_docs_id_conf_eq_doc_1_summary_contract_export_for_conf_eq_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_value_value_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_value_n_type_any_n_required_true_n_description_input_parameter_value_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_conf_has_error_category_from_assert_function_path_export_conf_has_error_category_params_subject_category_required_true_docs_id_conf_has_error_category_doc_1_summary_contract_export_for_conf_has_error_category_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_category_category_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_category_n_type_any_n_required_true_n_description_input_parameter_category_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_conf_json_type_is_from_assert_function_path_export_conf_json_type_is_params_subject_type_name_required_true_docs_id_conf_json_type_is_doc_1_summary_contract_export_for_conf_json_type_is_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_type_name_type_name_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_type_name_n_type_any_n_required_true_n_description_input_parameter_type_name_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.assertion.core.spec.1
    direction: bidirectional
    profile: default
services:
- id: svc.lib.assertion.core.spec.1
  consumes:
  - act.lib.assertion.core.spec.1
```
