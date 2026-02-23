```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: domain.os.exec_ok
      from: assert.function
      path: /__export__domain.os.exec_ok
      params:
      - command
      - timeout_ms
      required: true
      docs:
      - id: domain.os.exec_ok.doc.1
        summary: Contract export for `domain.os.exec_ok`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  command: \"<command>\"\n  timeout_ms: \"<timeout_ms>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\n- params:\
          \ - name: command\n  type: any\n  required: true\n  description: Input parameter\
          \ `command`.\\ n- name: timeout_ms\n  type: any\n  required: true\n  description:\
          \ Input parameter `timeout_ms`.\n- returns: type: any\ndescription: Result\
          \ payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input\
          \ payload does not satisfy contract shape requirements.\n  category: schema\n\
          - portability: python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime\
          \ behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-OS-001-001-DOMAIN-OS-EXEC-OK
    docs:
    - summary: Case `LIB-DOMAIN-OS-001-001-DOMAIN-OS-EXEC-OK` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.os.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.os.exec_ok
        assert:
          std.logic.eq:
          - ops.os.exec:
            - var: command
            - var: timeout_ms
          - 0
  - id: LIB-DOMAIN-OS-001-002-DOMAIN-OS-EXEC-CAPTURE-CODE
    docs:
    - summary: Case `LIB-DOMAIN-OS-001-002-DOMAIN-OS-EXEC-CAPTURE-CODE` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.os.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.os.exec_capture_code
        assert:
          std.logic.eq:
          - std.object.get:
            - ops.os.exec_capture:
              - var: command
              - var: timeout_ms
            - code
          - var: expected_code
  - id: LIB-DOMAIN-OS-001-003-DOMAIN-OS-ENV-HAS
    docs:
    - summary: Case `LIB-DOMAIN-OS-001-003-DOMAIN-OS-ENV-HAS` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.os.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.os.env_has
        assert:
          ops.os.env_has:
          - var: key
adapters:
- type: beta.exports_as_domain_os_exec_ok_from_assert_function_path_export_domain_os_exec_ok_params_command_timeout_ms_required_true_docs_id_domain_os_exec_ok_doc_1_summary_contract_export_for_domain_os_exec_ok_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_command_command_n_timeout_ms_timeout_ms_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_command_n_type_any_n_required_true_n_description_input_parameter_command_n_name_timeout_ms_n_type_any_n_required_true_n_description_input_parameter_timeout_ms_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.os.core.spec.1
    profile: default
- type: beta.exports_as_domain_os_exec_capture_code_from_assert_function_path_export_domain_os_exec_capture_code_params_command_timeout_ms_expected_code_required_true_docs_id_domain_os_exec_capture_code_doc_1_summary_contract_export_for_domain_os_exec_capture_code_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_command_command_n_timeout_ms_timeout_ms_n_expected_code_expected_code_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_command_n_type_any_n_required_true_n_description_input_parameter_command_n_name_timeout_ms_n_type_any_n_required_true_n_description_input_parameter_timeout_ms_n_name_expected_code_n_type_any_n_required_true_n_description_input_parameter_expected_code_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.os.core.spec.2
    profile: default
- type: beta.exports_as_domain_os_env_has_from_assert_function_path_export_domain_os_env_has_params_key_required_true_docs_id_domain_os_env_has_doc_1_summary_contract_export_for_domain_os_env_has_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_key_key_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_key_n_type_any_n_required_true_n_description_input_parameter_key_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.os.core.spec.3
    profile: default
services:
- id: svc.lib.os.core.spec.1
  consumes:
  - act.lib.os.core.spec.1
- id: svc.lib.os.core.spec.2
  consumes:
  - act.lib.os.core.spec.2
- id: svc.lib.os.core.spec.3
  consumes:
  - act.lib.os.core.spec.3
```


