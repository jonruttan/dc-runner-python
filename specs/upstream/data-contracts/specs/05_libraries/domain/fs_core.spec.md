```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: domain.fs.sort_spec_files
      from: assert.function
      path: /__export__domain.fs.sort_spec_files
      params:
      - paths
      required: true
      docs:
      - id: domain.fs.sort_spec_files.doc.1
        summary: Contract export for `domain.fs.sort_spec_files`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  paths: \"<paths>\"\nexpected: \"<result>\"\\ nnotes:\
          \ Replace with a concrete scenario.\n- params: - name: paths\n  type: any\n\
          \  required: true\n  description: Input parameter `paths`.\n- returns: type:\
          \ any\ndescription: Result payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n\
          \  when: Input payload does not satisfy contract shape requirements.\n \
          \ category: schema\n- portability: python: true\nphp: true\nrust: true\\\
          \ nnotes: Confirm per-runtime behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-FS-001-001-DOMAIN-FS-IS-DOCS-SPEC-FILE
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-001-DOMAIN-FS-IS-DOCS-SPEC-FILE` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.is_docs_spec_file
        assert:
          std.logic.and:
          - ops.fs.path.within:
            - /docs
            - ops.fs.path.normalize:
              - var: path
          - std.string.ends_with:
            - ops.fs.path.normalize:
              - var: path
            - .spec.md
  - id: LIB-DOMAIN-FS-001-002-DOMAIN-FS-SORT-SPEC-FILES
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-002-DOMAIN-FS-SORT-SPEC-FILES` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.sort_spec_files
        assert:
          ops.fs.path.sort:
          - ops.fs.glob.filter:
            - var: paths
            - '*.spec.md'
  - id: LIB-DOMAIN-FS-001-003-DOMAIN-FS-JSON-GET-OR-TEXT
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-003-DOMAIN-FS-JSON-GET-OR-TEXT` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.json_get_or_text
        assert:
          ops.fs.json.get_or:
          - ops.fs.json.parse:
            - var: json_text
          - var: path_segments
          - var: fallback
  - id: LIB-DOMAIN-FS-001-004-DOMAIN-FS-JSON-HAS-PATH-TEXT
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-004-DOMAIN-FS-JSON-HAS-PATH-TEXT` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.json_has_path_text
        assert:
          ops.fs.json.has_path:
          - ops.fs.json.parse:
            - var: json_text
          - var: path_segments
  - id: LIB-DOMAIN-FS-001-005-DOMAIN-FS-GLOB-ANY-SPEC-FILES
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-005-DOMAIN-FS-GLOB-ANY-SPEC-FILES` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.glob_any_spec_files
        assert:
          ops.fs.glob.any:
          - var: paths
          - '*.spec.md'
  - id: LIB-DOMAIN-FS-001-006-DOMAIN-FS-FILE-EXT-EQ
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-006-DOMAIN-FS-FILE-EXT-EQ` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.file_ext_eq
        assert:
          ops.fs.path.has_ext:
          - ops.fs.file.path:
            - var: meta
          - var: ext
  - id: LIB-DOMAIN-FS-001-007-DOMAIN-FS-JSON-GET-TEXT
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-007-DOMAIN-FS-JSON-GET-TEXT` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.json_get_text
        assert:
          ops.fs.json.get:
          - ops.fs.json.parse:
            - var: json_text
          - var: path_segments
  - id: LIB-DOMAIN-FS-001-008-DOMAIN-FS-JSON-PATH-EQ-TEXT
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-008-DOMAIN-FS-JSON-PATH-EQ-TEXT` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.json_path_eq_text
        assert:
          std.logic.eq:
          - call:
            - var: domain.fs.json_get_or_text
            - var: json_text
            - var: path_segments
          - var: expected
  - id: LIB-DOMAIN-FS-001-009-DOMAIN-FS-GLOB-FILTER
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-009-DOMAIN-FS-GLOB-FILTER` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.glob_filter
        assert:
          ops.fs.glob.filter:
          - var: paths
          - var: pattern
  - id: LIB-DOMAIN-FS-001-010-DOMAIN-FS-GLOB-ALL
    docs:
    - summary: Case `LIB-DOMAIN-FS-001-010-DOMAIN-FS-GLOB-ALL` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.fs.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.fs.glob_all
        assert:
          ops.fs.glob.all:
          - var: paths
          - var: pattern
adapters:
- type: beta.exports_as_domain_fs_is_docs_spec_file_from_assert_function_path_export_domain_fs_is_docs_spec_file_params_path_required_true_docs_id_domain_fs_is_docs_spec_file_doc_1_summary_contract_export_for_domain_fs_is_docs_spec_file_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.1
    profile: default
- type: beta.exports_as_domain_fs_sort_spec_files_from_assert_function_path_export_domain_fs_sort_spec_files_params_paths_required_true_docs_id_domain_fs_sort_spec_files_doc_1_summary_contract_export_for_domain_fs_sort_spec_files_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_paths_paths_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_paths_n_type_any_n_required_true_n_description_input_parameter_paths_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.2
    profile: default
- type: beta.exports_as_domain_fs_json_get_or_text_from_assert_function_path_export_domain_fs_json_get_or_text_params_json_text_path_segments_fallback_required_true_docs_id_domain_fs_json_get_or_text_doc_1_summary_contract_export_for_domain_fs_json_get_or_text_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_json_text_json_text_n_path_segments_path_segments_n_fallback_fallback_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_json_text_n_type_any_n_required_true_n_description_input_parameter_json_text_n_name_path_segments_n_type_any_n_required_true_n_description_input_parameter_path_segments_n_name_fallback_n_type_any_n_required_true_n_description_input_parameter_fallback_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.3
    profile: default
- type: beta.exports_as_domain_fs_json_has_path_text_from_assert_function_path_export_domain_fs_json_has_path_text_params_json_text_path_segments_required_true_docs_id_domain_fs_json_has_path_text_doc_1_summary_contract_export_for_domain_fs_json_has_path_text_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_json_text_json_text_n_path_segments_path_segments_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_json_text_n_type_any_n_required_true_n_description_input_parameter_json_text_n_name_path_segments_n_type_any_n_required_true_n_description_input_parameter_path_segments_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.4
    profile: default
- type: beta.exports_as_domain_fs_glob_any_spec_files_from_assert_function_path_export_domain_fs_glob_any_spec_files_params_paths_required_true_docs_id_domain_fs_glob_any_spec_files_doc_1_summary_contract_export_for_domain_fs_glob_any_spec_files_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_paths_paths_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_paths_n_type_any_n_required_true_n_description_input_parameter_paths_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.5
    profile: default
- type: beta.exports_as_domain_fs_file_ext_eq_from_assert_function_path_export_domain_fs_file_ext_eq_params_meta_ext_required_true_docs_id_domain_fs_file_ext_eq_doc_1_summary_contract_export_for_domain_fs_file_ext_eq_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_meta_meta_n_ext_ext_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_meta_n_type_any_n_required_true_n_description_input_parameter_meta_n_name_ext_n_type_any_n_required_true_n_description_input_parameter_ext_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.6
    profile: default
- type: beta.exports_as_domain_fs_json_get_text_from_assert_function_path_export_domain_fs_json_get_text_params_json_text_path_segments_required_true_docs_id_domain_fs_json_get_text_doc_1_summary_contract_export_for_domain_fs_json_get_text_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_json_text_json_text_n_path_segments_path_segments_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_json_text_n_type_any_n_required_true_n_description_input_parameter_json_text_n_name_path_segments_n_type_any_n_required_true_n_description_input_parameter_path_segments_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.7
    profile: default
- type: beta.exports_as_domain_fs_json_path_eq_text_from_assert_function_path_export_domain_fs_json_path_eq_text_params_json_text_path_segments_expected_required_true_docs_id_domain_fs_json_path_eq_text_doc_1_summary_contract_export_for_domain_fs_json_path_eq_text_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_json_text_json_text_n_path_segments_path_segments_n_expected_expected_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_json_text_n_type_any_n_required_true_n_description_input_parameter_json_text_n_name_path_segments_n_type_any_n_required_true_n_description_input_parameter_path_segments_n_name_expected_n_type_any_n_required_true_n_description_input_parameter_expected_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.8
    profile: default
- type: beta.exports_as_domain_fs_glob_filter_from_assert_function_path_export_domain_fs_glob_filter_params_paths_pattern_required_true_docs_id_domain_fs_glob_filter_doc_1_summary_contract_export_for_domain_fs_glob_filter_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_paths_paths_n_pattern_pattern_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_paths_n_type_any_n_required_true_n_description_input_parameter_paths_n_name_pattern_n_type_any_n_required_true_n_description_input_parameter_pattern_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.9
    profile: default
- type: beta.exports_as_domain_fs_glob_all_from_assert_function_path_export_domain_fs_glob_all_params_paths_pattern_required_true_docs_id_domain_fs_glob_all_doc_1_summary_contract_export_for_domain_fs_glob_all_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_paths_paths_n_pattern_pattern_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_paths_n_type_any_n_required_true_n_description_input_parameter_paths_n_name_pattern_n_type_any_n_required_true_n_description_input_parameter_pattern_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.fs.core.spec.10
    profile: default
services:
- id: svc.lib.fs.core.spec.1
  consumes:
  - act.lib.fs.core.spec.1
- id: svc.lib.fs.core.spec.2
  consumes:
  - act.lib.fs.core.spec.2
- id: svc.lib.fs.core.spec.3
  consumes:
  - act.lib.fs.core.spec.3
- id: svc.lib.fs.core.spec.4
  consumes:
  - act.lib.fs.core.spec.4
- id: svc.lib.fs.core.spec.5
  consumes:
  - act.lib.fs.core.spec.5
- id: svc.lib.fs.core.spec.6
  consumes:
  - act.lib.fs.core.spec.6
- id: svc.lib.fs.core.spec.7
  consumes:
  - act.lib.fs.core.spec.7
- id: svc.lib.fs.core.spec.8
  consumes:
  - act.lib.fs.core.spec.8
- id: svc.lib.fs.core.spec.9
  consumes:
  - act.lib.fs.core.spec.9
- id: svc.lib.fs.core.spec.10
  consumes:
  - act.lib.fs.core.spec.10
```









