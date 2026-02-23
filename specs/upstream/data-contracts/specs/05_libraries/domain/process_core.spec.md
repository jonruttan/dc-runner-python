```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    spec_lang:
      capabilities:
      - ops.os
    exports:
    - as: domain.process.exec_capture_ex_code
      from: assert.function
      path: /__export__domain.process.exec_capture_ex_code
      params:
      - command
      - options
      required: true
      docs:
      - id: domain.process.exec_capture_ex_code.doc.1
        summary: Contract export for `domain.process.exec_capture_ex_code`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  command: \"<command>\"\n  options: \"<options>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\n- params:\
          \ - name: command\n  type: any\n  required: true\n  description: Input parameter\
          \ `command`.\n- name: options\n  type: any\n  required: true\n  description:\
          \ Input parameter `options`.\n- returns: type: any\ndescription: Result\
          \ payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input\
          \ payload does not satisfy contract shape requirements.\n  category: schema\n\
          - portability: python: true\nphp: true\nrust: true\\ nnotes: Confirm per-runtime\
          \ behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-PROCESS-001-001-DOMAIN-PROCESS-EXEC-CAPTURE-EX-CODE
    docs:
    - summary: Case `LIB-DOMAIN-PROCESS-001-001-DOMAIN-PROCESS-EXEC-CAPTURE-EX-CODE`
        for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.process.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.process.exec_capture_ex_code
        assert:
          std.object.get:
          - ops.os.exec_capture_ex:
            - var: command
            - var: options
          - code
adapters:
- type: beta.spec_lang_capabilities_ops_os_exports_as_domain_process_exec_capture_ex_code_from_assert_function_path_export_domain_process_exec_capture_ex_code_params_command_options_required_true_docs_id_domain_process_exec_capture_ex_code_doc_1_summary_contract_export_for_domain_process_exec_capture_ex_code_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_command_command_n_options_options_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_command_n_type_any_n_required_true_n_description_input_parameter_command_n_name_options_n_type_any_n_required_true_n_description_input_parameter_options_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.process.core.spec.1
    direction: bidirectional
    profile: default
services:
- id: svc.lib.process.core.spec.1
  consumes:
  - act.lib.process.core.spec.1
```
