```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: domain.http.step_status_is
      from: assert.function
      path: /__export__domain.http.step_status_is
      params:
      - steps
      - step_id
      - expected
      docs:
      - id: domain.http.step_status_is.doc.1
        summary: Contract export for `domain.http.step_status_is`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  steps: \"<steps>\"\n  step_id: \"<step_id>\"\n\
          \  expected: \"<expected>\"\nexpected: \"<result>\"\nnotes: Replace with\
          \ a concrete scenario.\n- params: - name: steps\n  type: any\n  required:\
          \ true\n  description: Input parameter `steps`.\n- name: step_id\n  type:\
          \ any\n  required: true\n  description: Input parameter `step_id`.\\ n-\
          \ name: expected\n  type: any\n  required: true\n  description: Input parameter\
          \ `expected`.\n- returns: type: any\ndescription: Result payload for this\
          \ symbol.\\ n- errors: - code: SCHEMA_ERROR\n  when: Input payload does\
          \ not satisfy contract shape requirements.\n  category: schema\n- portability:\
          \ python: true\nphp: true\nrust: true\nnotes: Confirm per-runtime behavior\
          \ and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-HTTP-001-001-DOMAIN-HTTP-STATUS
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-001-DOMAIN-HTTP-STATUS` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.status
        assert:
          std.object.get:
          - std.object.get:
            - var: subject
            - value
          - status
  - id: LIB-DOMAIN-HTTP-001-002-DOMAIN-HTTP-STATUS-IN
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-002-DOMAIN-HTTP-STATUS-IN` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.status_in
        assert:
          std.collection.in:
          - std.object.get:
            - std.object.get:
              - var: subject
              - value
            - status
          - var: allowed
  - id: LIB-DOMAIN-HTTP-001-003-DOMAIN-HTTP-STATUS-IS
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-003-DOMAIN-HTTP-STATUS-IS` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.status_is
        assert:
          std.logic.eq:
          - std.object.get:
            - std.object.get:
              - var: subject
              - value
            - status
          - var: expected
  - id: LIB-DOMAIN-HTTP-001-004-DOMAIN-HTTP-STATUS-IS-UNAUTHORIZED
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-004-DOMAIN-HTTP-STATUS-IS-UNAUTHORIZED` for
        `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.status_is_unauthorized
        assert:
          lit:
            call:
            - var: domain.http.status_is
            - var: subject
            - 401
  - id: LIB-DOMAIN-HTTP-001-005-DOMAIN-HTTP-STATUS-IS-FORBIDDEN
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-005-DOMAIN-HTTP-STATUS-IS-FORBIDDEN` for
        `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.status_is_forbidden
        assert:
          lit:
            call:
            - var: domain.http.status_is
            - var: subject
            - 403
  - id: LIB-DOMAIN-HTTP-001-006-DOMAIN-HTTP-OK-2XX
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-006-DOMAIN-HTTP-OK-2XX` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.ok_2xx
        assert:
          std.logic.and:
          - std.logic.gte:
            - std.object.get:
              - std.object.get:
                - var: subject
                - value
              - status
            - 200
          - std.logic.lt:
            - std.object.get:
              - std.object.get:
                - var: subject
                - value
              - status
            - 300
  - id: LIB-DOMAIN-HTTP-001-007-DOMAIN-HTTP-HEADER-GET
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-007-DOMAIN-HTTP-HEADER-GET` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.header_get
        assert:
          std.object.get:
          - std.object.get:
            - std.object.get:
              - var: subject
              - value
            - headers
          - var: key
  - id: LIB-DOMAIN-HTTP-001-008-DOMAIN-HTTP-HEADER-CONTAINS
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-008-DOMAIN-HTTP-HEADER-CONTAINS` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.header_contains
        assert:
          std.string.contains:
          - std.object.get:
            - std.object.get:
              - std.object.get:
                - var: subject
                - value
              - headers
            - var: key
          - var: token
  - id: LIB-DOMAIN-HTTP-001-009-DOMAIN-HTTP-BODY-TEXT
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-009-DOMAIN-HTTP-BODY-TEXT` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.body_text
        assert:
          std.object.get:
          - std.object.get:
            - var: subject
            - value
          - body_text
  - id: LIB-DOMAIN-HTTP-001-010-DOMAIN-HTTP-BODY-JSON
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-010-DOMAIN-HTTP-BODY-JSON` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.body_json
        assert:
          std.object.get:
          - std.object.get:
            - var: subject
            - value
          - body_json
  - id: LIB-DOMAIN-HTTP-001-011-DOMAIN-HTTP-BODY-JSON-TYPE-IS
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-011-DOMAIN-HTTP-BODY-JSON-TYPE-IS` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.body_json_type_is
        assert:
          std.type.json_type:
          - std.object.get:
            - std.object.get:
              - var: subject
              - value
            - body_json
          - var: expected_type
  - id: LIB-DOMAIN-HTTP-001-012-DOMAIN-HTTP-BODY-JSON-HAS-KEY
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-012-DOMAIN-HTTP-BODY-JSON-HAS-KEY` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.body_json_has_key
        assert:
          std.object.has_key:
          - std.object.get:
            - std.object.get:
              - var: subject
              - value
            - body_json
          - var: key
  - id: LIB-DOMAIN-HTTP-001-013-DOMAIN-HTTP-AUTH-IS-OAUTH
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-013-DOMAIN-HTTP-AUTH-IS-OAUTH` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.auth_is_oauth
        assert:
          std.logic.eq:
          - std.object.get:
            - std.object.get:
              - var: subject
              - meta
            - auth_mode
          - oauth
  - id: LIB-DOMAIN-HTTP-001-014-DOMAIN-HTTP-OAUTH-TOKEN-SOURCE-IS
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-014-DOMAIN-HTTP-OAUTH-TOKEN-SOURCE-IS` for
        `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.oauth_token_source_is
        assert:
          std.logic.eq:
          - std.object.get:
            - std.object.get:
              - var: subject
              - meta
            - oauth_token_source
          - var: expected
  - id: LIB-DOMAIN-HTTP-001-015-DOMAIN-HTTP-HAS-BEARER-HEADER
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-015-DOMAIN-HTTP-HAS-BEARER-HEADER` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.has_bearer_header
        assert:
          std.string.starts_with:
          - std.object.get:
            - std.object.get:
              - std.object.get:
                - var: subject
                - value
              - headers
            - Authorization
          - 'Bearer '
  - id: LIB-DOMAIN-HTTP-001-015-DOMAIN-HTTP-OAUTH-SCOPE-REQUESTED
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-015-DOMAIN-HTTP-OAUTH-SCOPE-REQUESTED` for
        `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.oauth_scope_requested
        assert:
          std.logic.neq:
          - std.object.get:
            - std.object.get:
              - std.object.get:
                - var: subject
                - context
              - oauth
            - scope_requested
  - id: LIB-DOMAIN-HTTP-001-016-DOMAIN-HTTP-CORS-ALLOW-ORIGIN
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-016-DOMAIN-HTTP-CORS-ALLOW-ORIGIN` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.cors_allow_origin
        assert:
          std.object.get:
          - std.object.get:
            - std.object.get:
              - var: subject
              - value
            - cors
          - allow_origin
  - id: LIB-DOMAIN-HTTP-001-017-DOMAIN-HTTP-CORS-ALLOWS-METHOD
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-017-DOMAIN-HTTP-CORS-ALLOWS-METHOD` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.cors_allows_method
        assert:
          std.collection.includes:
          - std.object.get:
            - std.object.get:
              - std.object.get:
                - var: subject
                - value
              - cors
            - allow_methods
          - var: method_name
  - id: LIB-DOMAIN-HTTP-001-018-DOMAIN-HTTP-CORS-ALLOWS-HEADER
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-018-DOMAIN-HTTP-CORS-ALLOWS-HEADER` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.cors_allows_header
        assert:
          std.collection.includes:
          - std.object.get:
            - std.object.get:
              - std.object.get:
                - var: subject
                - value
              - cors
            - allow_headers
          - var: header_name
  - id: LIB-DOMAIN-HTTP-001-019-DOMAIN-HTTP-CORS-CREDENTIALS-ENABLED
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-019-DOMAIN-HTTP-CORS-CREDENTIALS-ENABLED`
        for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.cors_credentials_enabled
        assert:
          std.logic.eq:
          - std.object.get:
            - std.object.get:
              - std.object.get:
                - var: subject
                - value
              - cors
            - allow_credentials
          - true
  - id: LIB-DOMAIN-HTTP-001-020-DOMAIN-HTTP-CORS-MAX-AGE-GTE
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-020-DOMAIN-HTTP-CORS-MAX-AGE-GTE` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.cors_max_age_gte
        assert:
          std.logic.gte:
          - std.object.get:
            - std.object.get:
              - std.object.get:
                - var: subject
                - value
              - cors
            - max_age
          - var: min_age
  - id: LIB-DOMAIN-HTTP-001-021-DOMAIN-HTTP-IS-PREFLIGHT-STEP
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-021-DOMAIN-HTTP-IS-PREFLIGHT-STEP` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.is_preflight_step
        assert:
          std.logic.eq:
          - std.object.get:
            - var: step
            - method
          - OPTIONS
  - id: LIB-DOMAIN-HTTP-001-022-DOMAIN-HTTP-STEP-BY-ID
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-022-DOMAIN-HTTP-STEP-BY-ID` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.step_by_id
        assert:
          std.collection.find:
          - fn:
            - - row
            - std.logic.eq:
              - std.object.get:
                - var: row
                - id
              - var: step_id
          - var: steps
  - id: LIB-DOMAIN-HTTP-001-023-DOMAIN-HTTP-STEP-STATUS-IS
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-023-DOMAIN-HTTP-STEP-STATUS-IS` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.step_status_is
        assert:
          std.logic.eq:
          - std.object.get:
            - call:
              - var: domain.http.step_by_id
              - var: steps
              - var: step_id
            - status
          - var: expected
  - id: LIB-DOMAIN-HTTP-001-024-DOMAIN-HTTP-STEP-BODY-JSON-GET
    docs:
    - summary: Case `LIB-DOMAIN-HTTP-001-024-DOMAIN-HTTP-STEP-BODY-JSON-GET` for `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.http.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.http.step_body_json_get
        assert:
          std.object.get:
          - std.object.get:
            - call:
              - var: domain.http.step_by_id
              - var: steps
              - var: step_id
            - body_json
          - var: field
adapters:
- type: beta.exports_as_domain_http_status_from_assert_function_path_export_domain_http_status_params_subject_docs_id_domain_http_status_doc_1_summary_contract_export_for_domain_http_status_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.1
    profile: default
- type: beta.exports_as_domain_http_status_in_from_assert_function_path_export_domain_http_status_in_params_subject_allowed_docs_id_domain_http_status_in_doc_1_summary_contract_export_for_domain_http_status_in_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_allowed_allowed_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_allowed_n_type_any_n_required_true_n_description_input_parameter_allowed_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.2
    profile: default
- type: beta.exports_as_domain_http_status_is_from_assert_function_path_export_domain_http_status_is_params_subject_expected_docs_id_domain_http_status_is_doc_1_summary_contract_export_for_domain_http_status_is_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_expected_expected_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_expected_n_type_any_n_required_true_n_description_input_parameter_expected_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.3
    profile: default
- type: beta.exports_as_domain_http_status_is_unauthorized_from_assert_function_path_export_domain_http_status_is_unauthorized_params_subject_docs_id_domain_http_status_is_unauthorized_doc_1_summary_contract_export_for_domain_http_status_is_unauthorized_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.4
    profile: default
- type: beta.exports_as_domain_http_status_is_forbidden_from_assert_function_path_export_domain_http_status_is_forbidden_params_subject_docs_id_domain_http_status_is_forbidden_doc_1_summary_contract_export_for_domain_http_status_is_forbidden_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.5
    profile: default
- type: beta.exports_as_domain_http_ok_2xx_from_assert_function_path_export_domain_http_ok_2xx_params_subject_docs_id_domain_http_ok_2xx_doc_1_summary_contract_export_for_domain_http_ok_2xx_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.6
    profile: default
- type: beta.exports_as_domain_http_header_get_from_assert_function_path_export_domain_http_header_get_params_subject_key_docs_id_domain_http_header_get_doc_1_summary_contract_export_for_domain_http_header_get_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_key_key_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_key_n_type_any_n_required_true_n_description_input_parameter_key_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.7
    profile: default
- type: beta.exports_as_domain_http_header_contains_from_assert_function_path_export_domain_http_header_contains_params_subject_key_token_docs_id_domain_http_header_contains_doc_1_summary_contract_export_for_domain_http_header_contains_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_key_key_n_token_token_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_key_n_type_any_n_required_true_n_description_input_parameter_key_n_name_token_n_type_any_n_required_true_n_description_input_parameter_token_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.8
    profile: default
- type: beta.exports_as_domain_http_body_text_from_assert_function_path_export_domain_http_body_text_params_subject_docs_id_domain_http_body_text_doc_1_summary_contract_export_for_domain_http_body_text_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.9
    profile: default
- type: beta.exports_as_domain_http_body_json_from_assert_function_path_export_domain_http_body_json_params_subject_docs_id_domain_http_body_json_doc_1_summary_contract_export_for_domain_http_body_json_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.10
    profile: default
- type: beta.exports_as_domain_http_body_json_type_is_from_assert_function_path_export_domain_http_body_json_type_is_params_subject_expected_type_docs_id_domain_http_body_json_type_is_doc_1_summary_contract_export_for_domain_http_body_json_type_is_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_expected_type_expected_type_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_expected_type_n_type_any_n_required_true_n_description_input_parameter_expected_type_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.11
    profile: default
- type: beta.exports_as_domain_http_body_json_has_key_from_assert_function_path_export_domain_http_body_json_has_key_params_subject_key_docs_id_domain_http_body_json_has_key_doc_1_summary_contract_export_for_domain_http_body_json_has_key_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_key_key_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_key_n_type_any_n_required_true_n_description_input_parameter_key_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.12
    profile: default
- type: beta.exports_as_domain_http_auth_is_oauth_from_assert_function_path_export_domain_http_auth_is_oauth_params_subject_docs_id_domain_http_auth_is_oauth_doc_1_summary_contract_export_for_domain_http_auth_is_oauth_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.13
    profile: default
- type: beta.exports_as_domain_http_oauth_token_source_is_from_assert_function_path_export_domain_http_oauth_token_source_is_params_subject_expected_docs_id_domain_http_oauth_token_source_is_doc_1_summary_contract_export_for_domain_http_oauth_token_source_is_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_expected_expected_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_expected_n_type_any_n_required_true_n_description_input_parameter_expected_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.14
    profile: default
- type: beta.exports_as_domain_http_has_bearer_header_from_assert_function_path_export_domain_http_has_bearer_header_params_subject_docs_id_domain_http_has_bearer_header_doc_1_summary_contract_export_for_domain_http_has_bearer_header_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.15
    profile: default
- type: beta.exports_as_domain_http_oauth_scope_requested_from_assert_function_path_export_domain_http_oauth_scope_requested_params_subject_docs_id_domain_http_oauth_scope_requested_doc_1_summary_contract_export_for_domain_http_oauth_scope_requested_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.16
    profile: default
- type: beta.exports_as_domain_http_cors_allow_origin_from_assert_function_path_export_domain_http_cors_allow_origin_params_subject_docs_id_domain_http_cors_allow_origin_doc_1_summary_contract_export_for_domain_http_cors_allow_origin_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.17
    profile: default
- type: beta.exports_as_domain_http_cors_allows_method_from_assert_function_path_export_domain_http_cors_allows_method_params_subject_method_name_docs_id_domain_http_cors_allows_method_doc_1_summary_contract_export_for_domain_http_cors_allows_method_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_method_name_method_name_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_method_name_n_type_any_n_required_true_n_description_input_parameter_method_name_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.18
    profile: default
- type: beta.exports_as_domain_http_cors_allows_header_from_assert_function_path_export_domain_http_cors_allows_header_params_subject_header_name_docs_id_domain_http_cors_allows_header_doc_1_summary_contract_export_for_domain_http_cors_allows_header_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_header_name_header_name_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_header_name_n_type_any_n_required_true_n_description_input_parameter_header_name_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.19
    profile: default
- type: beta.exports_as_domain_http_cors_credentials_enabled_from_assert_function_path_export_domain_http_cors_credentials_enabled_params_subject_docs_id_domain_http_cors_credentials_enabled_doc_1_summary_contract_export_for_domain_http_cors_credentials_enabled_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.20
    profile: default
- type: beta.exports_as_domain_http_cors_max_age_gte_from_assert_function_path_export_domain_http_cors_max_age_gte_params_subject_min_age_docs_id_domain_http_cors_max_age_gte_doc_1_summary_contract_export_for_domain_http_cors_max_age_gte_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_subject_subject_n_min_age_min_age_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_subject_n_type_any_n_required_true_n_description_input_parameter_subject_n_name_min_age_n_type_any_n_required_true_n_description_input_parameter_min_age_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.21
    profile: default
- type: beta.exports_as_domain_http_is_preflight_step_from_assert_function_path_export_domain_http_is_preflight_step_params_step_docs_id_domain_http_is_preflight_step_doc_1_summary_contract_export_for_domain_http_is_preflight_step_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_step_step_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_step_n_type_any_n_required_true_n_description_input_parameter_step_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.22
    profile: default
- type: beta.exports_as_domain_http_step_by_id_from_assert_function_path_export_domain_http_step_by_id_params_steps_step_id_docs_id_domain_http_step_by_id_doc_1_summary_contract_export_for_domain_http_step_by_id_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_steps_steps_n_step_id_step_id_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_steps_n_type_any_n_required_true_n_description_input_parameter_steps_n_name_step_id_n_type_any_n_required_true_n_description_input_parameter_step_id_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.23
    profile: default
- type: beta.exports_as_domain_http_step_status_is_from_assert_function_path_export_domain_http_step_status_is_params_steps_step_id_expected_docs_id_domain_http_step_status_is_doc_1_summary_contract_export_for_domain_http_step_status_is_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_steps_steps_n_step_id_step_id_n_expected_expected_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_steps_n_type_any_n_required_true_n_description_input_parameter_steps_n_name_step_id_n_type_any_n_required_true_n_description_input_parameter_step_id_n_name_expected_n_type_any_n_required_true_n_description_input_parameter_expected_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.24
    profile: default
- type: beta.exports_as_domain_http_step_body_json_get_from_assert_function_path_export_domain_http_step_body_json_get_params_steps_step_id_field_docs_id_domain_http_step_body_json_get_doc_1_summary_contract_export_for_domain_http_step_body_json_get_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_steps_steps_n_step_id_step_id_n_field_field_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_steps_n_type_any_n_required_true_n_description_input_parameter_steps_n_name_step_id_n_type_any_n_required_true_n_description_input_parameter_step_id_n_name_field_n_type_any_n_required_true_n_description_input_parameter_field_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.http.core.spec.25
    profile: default
services:
- id: svc.lib.http.core.spec.1
  consumes:
  - act.lib.http.core.spec.1
- id: svc.lib.http.core.spec.2
  consumes:
  - act.lib.http.core.spec.2
- id: svc.lib.http.core.spec.3
  consumes:
  - act.lib.http.core.spec.3
- id: svc.lib.http.core.spec.4
  consumes:
  - act.lib.http.core.spec.4
- id: svc.lib.http.core.spec.5
  consumes:
  - act.lib.http.core.spec.5
- id: svc.lib.http.core.spec.6
  consumes:
  - act.lib.http.core.spec.6
- id: svc.lib.http.core.spec.7
  consumes:
  - act.lib.http.core.spec.7
- id: svc.lib.http.core.spec.8
  consumes:
  - act.lib.http.core.spec.8
- id: svc.lib.http.core.spec.9
  consumes:
  - act.lib.http.core.spec.9
- id: svc.lib.http.core.spec.10
  consumes:
  - act.lib.http.core.spec.10
- id: svc.lib.http.core.spec.11
  consumes:
  - act.lib.http.core.spec.11
- id: svc.lib.http.core.spec.12
  consumes:
  - act.lib.http.core.spec.12
- id: svc.lib.http.core.spec.13
  consumes:
  - act.lib.http.core.spec.13
- id: svc.lib.http.core.spec.14
  consumes:
  - act.lib.http.core.spec.14
- id: svc.lib.http.core.spec.15
  consumes:
  - act.lib.http.core.spec.15
- id: svc.lib.http.core.spec.16
  consumes:
  - act.lib.http.core.spec.16
- id: svc.lib.http.core.spec.17
  consumes:
  - act.lib.http.core.spec.17
- id: svc.lib.http.core.spec.18
  consumes:
  - act.lib.http.core.spec.18
- id: svc.lib.http.core.spec.19
  consumes:
  - act.lib.http.core.spec.19
- id: svc.lib.http.core.spec.20
  consumes:
  - act.lib.http.core.spec.20
- id: svc.lib.http.core.spec.21
  consumes:
  - act.lib.http.core.spec.21
- id: svc.lib.http.core.spec.22
  consumes:
  - act.lib.http.core.spec.22
- id: svc.lib.http.core.spec.23
  consumes:
  - act.lib.http.core.spec.23
- id: svc.lib.http.core.spec.24
  consumes:
  - act.lib.http.core.spec.24
- id: svc.lib.http.core.spec.25
  consumes:
  - act.lib.http.core.spec.25
```
























