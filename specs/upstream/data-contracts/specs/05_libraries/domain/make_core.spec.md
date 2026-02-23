```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: make.has_target
      from: assert.function
      path: /__export__make.has_target
      params:
      - subject
      - target
      required: true
      docs:
      - id: make.has_target.doc.1
        summary: Contract export for `make.has_target`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  subject: \"<subject>\"\n  target: \"<target>\"\n\
          expected: \"<result>\"\nnotes: Replace with a concrete scenario.\\ n- params:\
          \ - name: subject\n  type: any\n  required: true\n  description: Input parameter\
          \ `subject`.\n- name: target\n  type: any\n  required: true\n  description:\
          \ Input parameter `target`.\n- returns: type: any\ndescription: Result payload\
          \ for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input payload\
          \ does not satisfy contract shape requirements.\n  category: schema\\ n-\
          \ portability: python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime\
          \ behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-MAKE-001
    title: makefile projection helper functions
    docs:
    - summary: Case `LIB-DOMAIN-MAKE-001` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.make.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__make.has_target
        assert:
          std.string.contains:
          - std.object.get:
            - var: subject
            - value
          - var: target
adapters:
- type: beta.exports_as_make_has_target_from_assert_function_path_export_make_has_target_params_subject_target_required_true_docs_id_make_has_target_doc_1_summary_contract_export_for_make_has_target_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_target_target_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_target_n_type_any_n_required_true_n_description_input_parameter_target_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.make.core.spec.1
    direction: bidirectional
    profile: default
services:
- id: svc.lib.make.core.spec.1
  consumes:
  - act.lib.make.core.spec.1
```
