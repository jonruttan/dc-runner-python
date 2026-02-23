```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: domain.yaml.stringify
      from: assert.function
      path: /__export__domain.yaml.stringify
      params:
      - value
      required: true
      docs:
      - id: domain.yaml.stringify.doc.1
        summary: Contract export for `domain.yaml.stringify`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  value: \"<value>\"\nexpected: \"<result>\"\nnotes:\
          \ Replace with a concrete scenario.\\ n- params: - name: value\n  type:\
          \ any\n  required: true\n  description: Input parameter `value`.\n- returns:\
          \ type: any\ndescription: Result payload for this symbol.\n- errors: - code:\
          \ SCHEMA_ERROR\n  when: Input payload does not satisfy contract shape requirements.\n\
          \  category: schema\n- portability: python: true\nphp: true\nrust: true\n\
          notes: Confirm per-runtime behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-YAML-001-001-DOMAIN-YAML-PARSE-GET-OR
    docs:
    - summary: Case `LIB-DOMAIN-YAML-001-001-DOMAIN-YAML-PARSE-GET-OR` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.yaml.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.yaml.parse_get_or
        assert:
          ops.fs.yaml.get_or:
          - ops.fs.yaml.parse:
            - var: yaml_text
          - var: path_segments
          - var: fallback
  - id: LIB-DOMAIN-YAML-001-002-DOMAIN-YAML-STRINGIFY
    docs:
    - summary: Case `LIB-DOMAIN-YAML-001-002-DOMAIN-YAML-STRINGIFY` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.yaml.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.yaml.stringify
        assert:
          ops.fs.yaml.stringify:
          - var: value
adapters:
- type: beta.exports_as_domain_yaml_parse_get_or_from_assert_function_path_export_domain_yaml_parse_get_or_params_yaml_text_path_segments_fallback_required_true_docs_id_domain_yaml_parse_get_or_doc_1_summary_contract_export_for_domain_yaml_parse_get_or_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_yaml_text_yaml_text_n_path_segments_path_segments_n_fallback_fallback_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_yaml_text_n_type_any_n_required_true_n_description_input_parameter_yaml_text_n_name_path_segments_n_type_any_n_required_true_n_description_input_parameter_path_segments_n_name_fallback_n_type_any_n_required_true_n_description_input_parameter_fallback_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.yaml.core.spec.1
    profile: default
- type: beta.exports_as_domain_yaml_stringify_from_assert_function_path_export_domain_yaml_stringify_params_value_required_true_docs_id_domain_yaml_stringify_doc_1_summary_contract_export_for_domain_yaml_stringify_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_value_value_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_value_n_type_any_n_required_true_n_description_input_parameter_value_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.yaml.core.spec.2
    profile: default
services:
- id: svc.lib.yaml.core.spec.1
  consumes:
  - act.lib.yaml.core.spec.1
- id: svc.lib.yaml.core.spec.2
  consumes:
  - act.lib.yaml.core.spec.2
```

