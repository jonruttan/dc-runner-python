```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    check:
      profile: text.file
      config: {}
    use:
    - ref: '#LIB-PATH-001-001-PATH-NORMALIZE-SLASHES'
      as: lib_path_normalize
      symbols:
      - path.normalize_slashes
    exports:
    - as: path.segments
      from: assert.function
      path: /__export__path.segments
      params:
      - path
      docs:
      - id: path.segments.doc.1
        summary: Contract export for `path.segments`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  path: \"<path>\"\nexpected: \"<result>\"\nnotes:\
          \ Replace with a concrete scenario.\n- params: - name: path\n  type: any\n\
          \  required: true\n  description: Input parameter `path`.\n- returns: type:\
          \ any\ndescription: Result payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n\
          \  when: Input payload does not satisfy contract shape requirements.\n \
          \ category: schema\n- portability: python: true\nphp: true\nrust: true\n\
          notes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: path.trim_dot
      from: assert.function
      path: /__export__path.trim_dot
      params:
      - path
      docs:
      - id: path.trim_dot.doc.1
        summary: Contract export for `path.trim_dot`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  path: \"<path>\"\nexpected: \"<result>\"\nnotes:\
          \ Replace with a concrete scenario.\\ n- params: - name: path\n  type: any\n\
          \  required: true\n  description: Input parameter `path`.\n- returns: type:\
          \ any\ndescription: Result payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n\
          \  when: Input payload does not satisfy contract shape requirements.\n \
          \ category: schema\n- portability: python: true\\ nphp: true\nrust: true\n\
          notes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: path.dirname
      from: assert.function
      path: /__export__path.dirname
      params:
      - path
      docs:
      - id: path.dirname.doc.1
        summary: Contract export for `path.dirname`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  path: \"<path>\"\nexpected: \"<result>\"\nnotes:\
          \ Replace with a concrete scenario.\n- params: - name: path\n  type: any\n\
          \  required: true\n  description: Input parameter `path`.\n- returns: type:\
          \ any\ndescription: Result payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n\
          \  when: Input payload does not satisfy contract shape requirements.\n \
          \ category: schema\n- portability: python: true\nphp: true\\ nrust: true\n\
          notes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: path.has_extension
      from: assert.function
      path: /__export__path.has_extension
      params:
      - path
      - ext
      docs:
      - id: path.has_extension.doc.1
        summary: Contract export for `path.has_extension`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  path: \"<path>\"\n  ext: \"<ext>\"\nexpected: \"\
          <result>\"\nnotes: Replace with a concrete scenario.\n- params: - name:\
          \ path\n  type: any\n  required: true\n  description: Input parameter `path`.\\\
          \ n- name: ext\n  type: any\n  required: true\n  description: Input parameter\
          \ `ext`.\n- returns: type: any\ndescription: Result payload for this symbol.\\\
          \ n- errors: - code: SCHEMA_ERROR\n  when: Input payload does not satisfy\
          \ contract shape requirements.\n  category: schema\n- portability: python:\
          \ true\nphp: true\nrust: true\nnotes: Confirm per-runtime behavior and caveats."
        since: v1
    - as: path.is_under
      from: assert.function
      path: /__export__path.is_under
      params:
      - path
      - prefix
      docs:
      - id: path.is_under.doc.1
        summary: Contract export for `path.is_under`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  path: \"<path>\"\n  prefix: \"<prefix>\"\nexpected:\
          \ \"<result>\"\nnotes: Replace with a concrete scenario.\n- params: - name:\
          \ path\n  type: any\n  required: true\n  description: Input parameter `path`.\n\
          - name: prefix\n  type: any\n  required: true\n  description: Input parameter\
          \ `prefix`.\n- returns: type: any\ndescription: Result payload for this\
          \ symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input payload does not\
          \ satisfy contract shape requirements.\n  category: schema\n- portability:\
          \ python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime behavior\
          \ and caveats."
        since: v1
    - as: path.matches
      from: assert.function
      path: /__export__path.matches
      params:
      - path
      - pattern
      docs:
      - id: path.matches.doc.1
        summary: Contract export for `path.matches`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  path: \"<path>\"\n  pattern: \"<pattern>\"\nexpected:\
          \ \"<result>\"\nnotes: Replace with a concrete scenario.\\ n- params: -\
          \ name: path\n  type: any\n  required: true\n  description: Input parameter\
          \ `path`.\n- name: pattern\n  type: any\n  required: true\n  description:\
          \ Input parameter `pattern`.\n- returns: type: any\ndescription: Result\
          \ payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when: Input\
          \ payload does not satisfy contract shape requirements.\n  category: schema\n\
          - portability: python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime\
          \ behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-PATH-001-001-PATH-NORMALIZE-SLASHES
    docs:
    - summary: Case `LIB-PATH-001-001-PATH-NORMALIZE-SLASHES` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: path.path.core
      module: path
      stability: alpha
      owner: data-contracts
      tags:
      - path
    type: contract.export
    asserts:
      checks:
      - id: __export__path.normalize_slashes
        assert:
          std.string.replace:
          - var: path
          - \
          - /
      - id: __export__path.trim_dot
        assert:
          std.string.replace:
          - var: path
          - ./
          - ''
      - id: __export__path.dirname
        assert:
          lit:
            let:
            - lit:
              - - segs
                - call:
                  - var: path.segments
                  - var: path
            - if:
              - std.logic.lte:
                - std.collection.len:
                  - var: segs
                - 1
              - ''
              - std.string.join:
                - std.collection.slice:
                  - 0
                  - std.math.sub:
                    - std.collection.len:
                      - var: segs
                    - 1
                  - var: segs
                - /
      - id: __export__path.has_extension
        assert:
          std.logic.eq:
          - call:
            - var: path.extension
            - var: path
          - var: ext
      - id: __export__path.is_under
        assert:
          std.string.starts_with:
          - call:
            - var: path.normalize_slashes
            - var: path
          - call:
            - var: path.normalize_slashes
            - var: prefix
      - id: __export__path.matches
        assert:
          std.string.regex_match:
          - call:
            - var: path.normalize_slashes
            - var: path
          - var: pattern
  - id: LIB-PATH-001-002-PATH-SEGMENTS
    docs:
    - summary: Case `LIB-PATH-001-002-PATH-SEGMENTS` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: path.path.core
      module: path
      stability: alpha
      owner: data-contracts
      tags:
      - path
    type: contract.export
    asserts:
      checks:
      - id: __export__path.segments
        assert:
          std.string.split:
          - call:
            - var: path.normalize_slashes
            - var: path
          - /
      - id: __export__path.trim_dot
        assert:
          std.string.replace:
          - var: path
          - ./
          - ''
      - id: __export__path.dirname
        assert:
          lit:
            let:
            - lit:
              - - segs
                - call:
                  - var: path.segments
                  - var: path
            - if:
              - std.logic.lte:
                - std.collection.len:
                  - var: segs
                - 1
              - ''
              - std.string.join:
                - std.collection.slice:
                  - 0
                  - std.math.sub:
                    - std.collection.len:
                      - var: segs
                    - 1
                  - var: segs
                - /
      - id: __export__path.has_extension
        assert:
          std.logic.eq:
          - call:
            - var: path.extension
            - var: path
          - var: ext
      - id: __export__path.is_under
        assert:
          std.string.starts_with:
          - call:
            - var: path.normalize_slashes
            - var: path
          - call:
            - var: path.normalize_slashes
            - var: prefix
      - id: __export__path.matches
        assert:
          std.string.regex_match:
          - call:
            - var: path.normalize_slashes
            - var: path
          - var: pattern
  - id: LIB-PATH-001-003-PATH-BASENAME
    docs:
    - summary: Case `LIB-PATH-001-003-PATH-BASENAME` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: path.path.core
      module: path
      stability: alpha
      owner: data-contracts
      tags:
      - path
    type: contract.export
    asserts:
      checks:
      - id: __export__path.basename
        assert:
          lit:
            let:
            - lit:
              - - segs
                - call:
                  - var: path.segments
                  - var: path
            - if:
              - std.collection.is_empty:
                - var: segs
              - ''
              - std.object.get:
                - var: segs
                - std.math.sub:
                  - std.collection.len:
                    - var: segs
                  - 1
      - id: __export__path.trim_dot
        assert:
          std.string.replace:
          - var: path
          - ./
          - ''
      - id: __export__path.dirname
        assert:
          lit:
            let:
            - lit:
              - - segs
                - call:
                  - var: path.segments
                  - var: path
            - if:
              - std.logic.lte:
                - std.collection.len:
                  - var: segs
                - 1
              - ''
              - std.string.join:
                - std.collection.slice:
                  - 0
                  - std.math.sub:
                    - std.collection.len:
                      - var: segs
                    - 1
                  - var: segs
                - /
      - id: __export__path.has_extension
        assert:
          std.logic.eq:
          - call:
            - var: path.extension
            - var: path
          - var: ext
      - id: __export__path.is_under
        assert:
          std.string.starts_with:
          - call:
            - var: path.normalize_slashes
            - var: path
          - call:
            - var: path.normalize_slashes
            - var: prefix
      - id: __export__path.matches
        assert:
          std.string.regex_match:
          - call:
            - var: path.normalize_slashes
            - var: path
          - var: pattern
  - id: LIB-PATH-001-004-PATH-EXTENSION
    docs:
    - summary: Case `LIB-PATH-001-004-PATH-EXTENSION` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: path.path.core
      module: path
      stability: alpha
      owner: data-contracts
      tags:
      - path
    type: contract.export
    asserts:
      checks:
      - id: __export__path.extension
        assert:
          lit:
            let:
            - lit:
              - - base
                - call:
                  - var: path.basename
                  - var: path
            - let:
              - lit:
                - - parts
                  - split:
                    - var: base
                    - .
              - if:
                - std.logic.lte:
                  - std.collection.len:
                    - var: parts
                  - 1
                - ''
                - std.object.get:
                  - var: parts
                  - std.math.sub:
                    - std.collection.len:
                      - var: parts
                    - 1
      - id: __export__path.trim_dot
        assert:
          std.string.replace:
          - var: path
          - ./
          - ''
      - id: __export__path.dirname
        assert:
          lit:
            let:
            - lit:
              - - segs
                - call:
                  - var: path.segments
                  - var: path
            - if:
              - std.logic.lte:
                - std.collection.len:
                  - var: segs
                - 1
              - ''
              - std.string.join:
                - std.collection.slice:
                  - 0
                  - std.math.sub:
                    - std.collection.len:
                      - var: segs
                    - 1
                  - var: segs
                - /
      - id: __export__path.has_extension
        assert:
          std.logic.eq:
          - call:
            - var: path.extension
            - var: path
          - var: ext
      - id: __export__path.is_under
        assert:
          std.string.starts_with:
          - call:
            - var: path.normalize_slashes
            - var: path
          - call:
            - var: path.normalize_slashes
            - var: prefix
      - id: __export__path.matches
        assert:
          std.string.regex_match:
          - call:
            - var: path.normalize_slashes
            - var: path
          - var: pattern
  - id: LIB-PATH-001-900-PATH-SMOKE
    type: contract.check
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.logic.eq:
          - call:
            - var: path.normalize_slashes
            - a\\b\\c.txt
          - a/b/c.txt
adapters:
- type: beta.exports_as_path_normalize_slashes_from_assert_function_path_export_path_normalize_slashes_params_path_docs_id_path_normalize_slashes_doc_1_summary_contract_export_for_path_normalize_slashes_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_trim_dot_from_assert_function_path_export_path_trim_dot_params_path_docs_id_path_trim_dot_doc_1_summary_contract_export_for_path_trim_dot_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_dirname_from_assert_function_path_export_path_dirname_params_path_docs_id_path_dirname_doc_1_summary_contract_export_for_path_dirname_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_has_extension_from_assert_function_path_export_path_has_extension_params_path_ext_docs_id_path_has_extension_doc_1_summary_contract_export_for_path_has_extension_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_ext_ext_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_ext_n_type_any_n_required_true_n_description_input_parameter_ext_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_is_under_from_assert_function_path_export_path_is_under_params_path_prefix_docs_id_path_is_under_doc_1_summary_contract_export_for_path_is_under_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_prefix_prefix_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_prefix_n_type_any_n_required_true_n_description_input_parameter_prefix_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_matches_from_assert_function_path_export_path_matches_params_path_pattern_docs_id_path_matches_doc_1_summary_contract_export_for_path_matches_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_pattern_pattern_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_pattern_n_type_any_n_required_true_n_description_input_parameter_pattern_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.path.core.spec.1
    profile: default
- type: beta.exports_as_path_segments_from_assert_function_path_export_path_segments_params_path_docs_id_path_segments_doc_1_summary_contract_export_for_path_segments_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_trim_dot_from_assert_function_path_export_path_trim_dot_params_path_docs_id_path_trim_dot_doc_1_summary_contract_export_for_path_trim_dot_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_dirname_from_assert_function_path_export_path_dirname_params_path_docs_id_path_dirname_doc_1_summary_contract_export_for_path_dirname_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_has_extension_from_assert_function_path_export_path_has_extension_params_path_ext_docs_id_path_has_extension_doc_1_summary_contract_export_for_path_has_extension_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_ext_ext_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_ext_n_type_any_n_required_true_n_description_input_parameter_ext_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_is_under_from_assert_function_path_export_path_is_under_params_path_prefix_docs_id_path_is_under_doc_1_summary_contract_export_for_path_is_under_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_prefix_prefix_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_prefix_n_type_any_n_required_true_n_description_input_parameter_prefix_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_matches_from_assert_function_path_export_path_matches_params_path_pattern_docs_id_path_matches_doc_1_summary_contract_export_for_path_matches_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_pattern_pattern_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_pattern_n_type_any_n_required_true_n_description_input_parameter_pattern_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.path.core.spec.2
    profile: default
- type: beta.exports_as_path_basename_from_assert_function_path_export_path_basename_params_path_docs_id_path_basename_doc_1_summary_contract_export_for_path_basename_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_trim_dot_from_assert_function_path_export_path_trim_dot_params_path_docs_id_path_trim_dot_doc_1_summary_contract_export_for_path_trim_dot_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_dirname_from_assert_function_path_export_path_dirname_params_path_docs_id_path_dirname_doc_1_summary_contract_export_for_path_dirname_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_has_extension_from_assert_function_path_export_path_has_extension_params_path_ext_docs_id_path_has_extension_doc_1_summary_contract_export_for_path_has_extension_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_ext_ext_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_ext_n_type_any_n_required_true_n_description_input_parameter_ext_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_is_under_from_assert_function_path_export_path_is_under_params_path_prefix_docs_id_path_is_under_doc_1_summary_contract_export_for_path_is_under_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_prefix_prefix_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_prefix_n_type_any_n_required_true_n_description_input_parameter_prefix_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_matches_from_assert_function_path_export_path_matches_params_path_pattern_docs_id_path_matches_doc_1_summary_contract_export_for_path_matches_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_pattern_pattern_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_pattern_n_type_any_n_required_true_n_description_input_parameter_pattern_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.path.core.spec.3
    profile: default
- type: beta.exports_as_path_extension_from_assert_function_path_export_path_extension_params_path_docs_id_path_extension_doc_1_summary_contract_export_for_path_extension_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_trim_dot_from_assert_function_path_export_path_trim_dot_params_path_docs_id_path_trim_dot_doc_1_summary_contract_export_for_path_trim_dot_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_dirname_from_assert_function_path_export_path_dirname_params_path_docs_id_path_dirname_doc_1_summary_contract_export_for_path_dirname_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_has_extension_from_assert_function_path_export_path_has_extension_params_path_ext_docs_id_path_has_extension_doc_1_summary_contract_export_for_path_has_extension_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_ext_ext_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_ext_n_type_any_n_required_true_n_description_input_parameter_ext_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_is_under_from_assert_function_path_export_path_is_under_params_path_prefix_docs_id_path_is_under_doc_1_summary_contract_export_for_path_is_under_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_prefix_prefix_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_prefix_n_type_any_n_required_true_n_description_input_parameter_prefix_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1_as_path_matches_from_assert_function_path_export_path_matches_params_path_pattern_docs_id_path_matches_doc_1_summary_contract_export_for_path_matches_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_path_path_n_pattern_pattern_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_path_n_type_any_n_required_true_n_description_input_parameter_path_n_name_pattern_n_type_any_n_required_true_n_description_input_parameter_pattern_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.path.core.spec.4
    profile: default
- type: beta.check_profile_text_file_config_use_ref_lib_path_001_001_path_normalize_slashes_as_lib_path_normalize_symbols_path_normalize_slashes
  actions:
  - id: act.lib.path.core.spec.5
    profile: default
services:
- id: svc.lib.path.core.spec.1
  consumes:
  - act.lib.path.core.spec.1
- id: svc.lib.path.core.spec.2
  consumes:
  - act.lib.path.core.spec.2
- id: svc.lib.path.core.spec.3
  consumes:
  - act.lib.path.core.spec.3
- id: svc.lib.path.core.spec.4
  consumes:
  - act.lib.path.core.spec.4
- id: svc.lib.path.core.spec.5
  consumes:
  - act.lib.path.core.spec.5
```




