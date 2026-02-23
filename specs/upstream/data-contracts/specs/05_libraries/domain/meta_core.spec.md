```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: domain.meta.has_artifact_target
      from: assert.function
      path: /__export__domain.meta.has_artifact_target
      params:
      - meta
      - target_name
      required: true
      docs:
      - id: domain.meta.has_artifact_target.doc.1
        summary: Contract export for `domain.meta.has_artifact_target`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  meta: \"<meta>\"\n  target_name: \"<target_name>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\n- params:\
          \ - name: meta\n  type: any\n  required: true\n  description: Input parameter\
          \ `meta`.\n- name: target_name\n  type: any\n  required: true\n  description:\
          \ Input parameter `target_name`.\n- returns: type: any\ndescription: Result\
          \ payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input\
          \ payload does not satisfy contract shape requirements.\n  category: schema\\\
          \ n- portability: python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime\
          \ behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-META-001-001-DOMAIN-META-CASE-ID-EQ
    docs:
    - summary: Case `LIB-DOMAIN-META-001-001-DOMAIN-META-CASE-ID-EQ` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.meta.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.meta.case_id_eq
        assert:
          std.logic.eq:
          - std.object.get:
            - std.object.get:
              - var: meta
              - case
            - id
          - var: case_id
  - id: LIB-DOMAIN-META-001-002-DOMAIN-META-HAS-ARTIFACT-TARGET
    docs:
    - summary: Case `LIB-DOMAIN-META-001-002-DOMAIN-META-HAS-ARTIFACT-TARGET` for
        `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.meta.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.meta.has_artifact_target
        assert:
          std.collection.includes:
          - std.object.get:
            - std.object.get:
              - var: meta
              - artifacts
            - target_keys
          - var: target_name
adapters:
- type: beta.exports_as_domain_meta_case_id_eq_from_assert_function_path_export_domain_meta_case_id_eq_params_meta_case_id_required_true_docs_id_domain_meta_case_id_eq_doc_1_summary_contract_export_for_domain_meta_case_id_eq_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_meta_meta_n_case_id_case_id_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_meta_n_type_any_n_required_true_n_description_input_parameter_meta_n_name_case_id_n_type_any_n_required_true_n_description_input_parameter_case_id_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.meta.core.spec.1
    profile: default
- type: beta.exports_as_domain_meta_has_artifact_target_from_assert_function_path_export_domain_meta_has_artifact_target_params_meta_target_name_required_true_docs_id_domain_meta_has_artifact_target_doc_1_summary_contract_export_for_domain_meta_has_artifact_target_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_meta_meta_n_target_name_target_name_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_meta_n_type_any_n_required_true_n_description_input_parameter_meta_n_name_target_name_n_type_any_n_required_true_n_description_input_parameter_target_name_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.meta.core.spec.2
    profile: default
services:
- id: svc.lib.meta.core.spec.1
  consumes:
  - act.lib.meta.core.spec.1
- id: svc.lib.meta.core.spec.2
  consumes:
  - act.lib.meta.core.spec.2
```

