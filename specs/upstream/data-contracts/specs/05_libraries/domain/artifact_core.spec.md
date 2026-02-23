```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: domain.artifact.write_yaml
      from: assert.function
      path: /__export__domain.artifact.write_yaml
      params:
      - path
      - value
      required: true
      docs:
      - id: domain.artifact.write_yaml.doc.1
        summary: Contract export for `domain.artifact.write_yaml`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  path: \"<path>\"\n  value: \"<value>\"\nexpected:\
          \ \"<result>\"\nnotes: Replace with a concrete scenario.\n- params: - name:\
          \ path\n  type: any\n  required: true\n  description: Input parameter `path`.\n\
          - name: value\n  type: any\n  required: true\n  description: Input parameter\
          \ `value`.\n- returns: type: any\ndescription: Result payload for this symbol.\n\
          - errors: - code: SCHEMA_ERROR\n  when: Input payload does not satisfy contract\
          \ shape requirements.\n  category: schema\n- portability: python: true\n\
          php: true\nrust: true\nnotes: Confirm per-runtime behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-ARTIFACT-001-001-DOMAIN-ARTIFACT-WRITE-YAML
    docs:
    - summary: Case `LIB-DOMAIN-ARTIFACT-001-001-DOMAIN-ARTIFACT-WRITE-YAML` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.artifact.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.artifact.write_yaml
        assert:
          ops.fs.file.set:
          - var: path
          - ops.fs.yaml.stringify:
            - var: value
  - id: LIB-DOMAIN-ARTIFACT-001-002-DOMAIN-ARTIFACT-APPEND-TEXT
    docs:
    - summary: Case `LIB-DOMAIN-ARTIFACT-001-002-DOMAIN-ARTIFACT-APPEND-TEXT` for
        `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.artifact.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.artifact.append_text
        assert:
          ops.fs.file.append:
          - var: path
          - var: content
adapters:
- type: beta.exports_as_domain_artifact_write_yaml_from_assert_function_path_export_domain_artifact_write_yaml_params_path_value_required_true_docs_id_domain_artifact_write_yaml_doc_1_summary_contract_export_for_domain_artifact_write_yaml_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_value_value_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_value_n_type_any_n_required_true_n_description_input_parameter_value_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.artifact.core.spec.1
    profile: default
- type: beta.exports_as_domain_artifact_append_text_from_assert_function_path_export_domain_artifact_append_text_params_path_content_required_true_docs_id_domain_artifact_append_text_doc_1_summary_contract_export_for_domain_artifact_append_text_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_content_content_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_content_n_type_any_n_required_true_n_description_input_parameter_content_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.artifact.core.spec.2
    profile: default
services:
- id: svc.lib.artifact.core.spec.1
  consumes:
  - act.lib.artifact.core.spec.1
- id: svc.lib.artifact.core.spec.2
  consumes:
  - act.lib.artifact.core.spec.2
```

