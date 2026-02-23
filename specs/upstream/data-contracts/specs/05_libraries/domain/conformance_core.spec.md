```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: domain.conformance.validate_report_errors
      from: assert.function
      path: /__export__domain.conformance.validate_report_errors
      params:
      - report
      required: true
      docs:
      - id: domain.conformance.validate_report_errors.doc.1
        summary: Contract export for `domain.conformance.validate_report_errors`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  report: \"<report>\"\nexpected: \"<result>\"\n\
          notes: Replace with a concrete scenario.\\ n- params: - name: report\n \
          \ type: any\n  required: true\n  description: Input parameter `report`.\n\
          - returns: type: any\ndescription: Result payload for this symbol.\n- errors:\
          \ - code: SCHEMA_ERROR\n  when: Input payload does not satisfy contract\
          \ shape requirements.\n  category: schema\n- portability: python: true\n\
          php: true\nrust: true\nnotes: Confirm per-runtime behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-CONFORMANCE-001-000-DOMAIN-CONFORMANCE-ERROR-WHEN-FALSE
    docs:
    - summary: Case `LIB-DOMAIN-CONFORMANCE-001-000-DOMAIN-CONFORMANCE-ERROR-WHEN-FALSE`
        for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.conformance.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.conformance.error_when_false
        assert:
          lit:
            if:
            - var: condition
            - lit: []
            - lit:
              - var: message
  - id: LIB-DOMAIN-CONFORMANCE-001-000A-DOMAIN-CONFORMANCE-REPORT-VERSION-IS-V1
    docs:
    - summary: Case `LIB-DOMAIN-CONFORMANCE-001-000A-DOMAIN-CONFORMANCE-REPORT-VERSION-IS-V1`
        for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.conformance.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.conformance.report_version_is_v1
        assert:
          std.logic.eq:
          - std.object.get:
            - var: report
            - version
          - 1
  - id: LIB-DOMAIN-CONFORMANCE-001-000B-DOMAIN-CONFORMANCE-REPORT-RESULTS-IS-LIST
    docs:
    - summary: Case `LIB-DOMAIN-CONFORMANCE-001-000B-DOMAIN-CONFORMANCE-REPORT-RESULTS-IS-LIST`
        for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.conformance.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.conformance.report_results_is_list
        assert:
          std.type.is_list:
          - std.object.get:
            - var: report
            - results
  - id: LIB-DOMAIN-CONFORMANCE-001-000C-DOMAIN-CONFORMANCE-VALIDATE-REPORT-ERRORS
    docs:
    - summary: Case `LIB-DOMAIN-CONFORMANCE-001-000C-DOMAIN-CONFORMANCE-VALIDATE-REPORT-ERRORS`
        for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.conformance.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.conformance.validate_report_errors
        assert:
          std.collection.concat:
          - if:
            - std.logic.eq:
              - std.object.get:
                - var: report
                - version
              - 1
            - lit: []
            - lit:
              - report.version must equal 1
          - if:
            - std.type.is_list:
              - std.object.get:
                - var: report
                - results
            - lit: []
            - lit:
              - report.results must be a list
adapters:
- type: beta.exports_as_domain_conformance_error_when_false_from_assert_function_path_export_domain_conformance_error_when_false_params_condition_message_required_true_docs_id_domain_conformance_error_when_false_doc_1_summary_contract_export_for_domain_conformance_error_when_false_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_condition_condition_n_message_message_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_condition_n_type_any_n_required_true_n_description_input_parameter_condition_n_name_message_n_type_any_n_required_true_n_description_input_parameter_message_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.conformance.core.spec.1
    profile: default
- type: beta.exports_as_domain_conformance_report_version_is_v1_from_assert_function_path_export_domain_conformance_report_version_is_v1_params_report_required_true_docs_id_domain_conformance_report_version_is_v1_doc_1_summary_contract_export_for_domain_conformance_report_version_is_v1_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_report_report_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_report_n_type_any_n_required_true_n_description_input_parameter_report_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.conformance.core.spec.2
    profile: default
- type: beta.exports_as_domain_conformance_report_results_is_list_from_assert_function_path_export_domain_conformance_report_results_is_list_params_report_required_true_docs_id_domain_conformance_report_results_is_list_doc_1_summary_contract_export_for_domain_conformance_report_results_is_list_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_report_report_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_report_n_type_any_n_required_true_n_description_input_parameter_report_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.conformance.core.spec.3
    profile: default
- type: beta.exports_as_domain_conformance_validate_report_errors_from_assert_function_path_export_domain_conformance_validate_report_errors_params_report_required_true_docs_id_domain_conformance_validate_report_errors_doc_1_summary_contract_export_for_domain_conformance_validate_report_errors_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_report_report_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_report_n_type_any_n_required_true_n_description_input_parameter_report_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.conformance.core.spec.4
    profile: default
services:
- id: svc.lib.conformance.core.spec.1
  consumes:
  - act.lib.conformance.core.spec.1
- id: svc.lib.conformance.core.spec.2
  consumes:
  - act.lib.conformance.core.spec.2
- id: svc.lib.conformance.core.spec.3
  consumes:
  - act.lib.conformance.core.spec.3
- id: svc.lib.conformance.core.spec.4
  consumes:
  - act.lib.conformance.core.spec.4
```



