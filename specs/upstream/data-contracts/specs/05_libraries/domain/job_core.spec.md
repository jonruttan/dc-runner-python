```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    spec_lang:
      capabilities:
      - ops.helper
    exports:
    - as: domain.job.scan_bundle_has_result
      from: assert.function
      path: /__export__domain.job.scan_bundle_has_result
      params:
      - scan_path
      - pattern
      docs:
      - id: domain.job.scan_bundle_has_result.doc.1
        summary: Contract export for `domain.job.scan_bundle_has_result`.
        audience: spec-authors
        status: active
        description: "Auto-generated metadata stub. Replace with authored reference\
          \ text.\n\nDocumentation metadata:\n- examples[]: title:\
          \ Basic usage\ninput:\n  scan_path: \"<scan_path>\"\n  pattern: \"<pattern>\"\
          \nexpected: \"<result>\"\nnotes: Replace with a concrete scenario.\n- params:\
          \ - name: scan_path\n  type: any\n  required: true\n  description: Input\
          \ parameter `scan_path`.\n- name: pattern\n  type: any\n  required: true\n\
          \  description: Input parameter `pattern`.\n- returns: type: any\ndescription:\
          \ Result payload for this symbol.\n- errors: - code: SCHEMA_ERROR\n  when:\
          \ Input payload does not satisfy contract shape requirements.\n  category:\
          \ schema\n- portability: python: true\nphp: true\nrust: true\\ nnotes: Confirm\
          \ per-runtime behavior and caveats."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-JOB-001-000A-DOMAIN-JOB-SCAN-BUNDLE-HAS-RESULT
    title: domain.job.scan_bundle_has_result
    purpose: Reusable helper-backed predicate for contract.job governance scan helper
      output.
    docs:
    - summary: Case `LIB-DOMAIN-JOB-001-000A-DOMAIN-JOB-SCAN-BUNDLE-HAS-RESULT` for
        `contract.export`.
      audience: spec-authors
      status: active
      description: Auto-generated root doc metadata stub. Replace with authored reference
        text.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.job.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      imports:
      - from: asset
        names:
        - subject
      checks:
      - id: __export__domain.job.scan_bundle_has_result
        assert:
          std.logic.neq:
          - std.object.get:
            - ops.helper.call:
              - lit: helper.governance.scan_bundle
              - lit:
                  path:
                    var: scan_path
                  patterns:
                  - var: pattern
            - scanned_files
adapters:
- type: beta.spec_lang_capabilities_ops_helper_exports_as_domain_job_scan_bundle_has_result_from_assert_function_path_export_domain_job_scan_bundle_has_result_params_scan_path_pattern_docs_id_domain_job_scan_bundle_has_result_doc_1_summary_contract_export_for_domain_job_scan_bundle_has_result_audience_spec_authors_status_active_description_auto_generated_metadata_stub_replace_with_authored_reference_text_n_nprior_doc_fields_migrated_to_description_n_examples_title_basic_usage_ninput_n_scan_path_scan_path_n_pattern_pattern_nexpected_result_nnotes_replace_with_a_concrete_scenario_n_params_name_scan_path_n_type_any_n_required_true_n_description_input_parameter_scan_path_n_name_pattern_n_type_any_n_required_true_n_description_input_parameter_pattern_n_returns_type_any_ndescription_result_payload_for_this_symbol_n_errors_code_schema_error_n_when_input_payload_does_not_satisfy_contract_shape_requirements_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_confirm_per_runtime_behavior_and_caveats_since_v1
  actions:
  - id: act.lib.job.core.spec.1
    direction: bidirectional
    profile: default
services:
- id: svc.lib.job.core.spec.1
  consumes:
  - act.lib.job.core.spec.1
```

