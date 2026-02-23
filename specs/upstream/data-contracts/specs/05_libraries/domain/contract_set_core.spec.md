```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: domain.contract_set.id
      from: assert.function
      path: /__export__domain.contract_set.id
      params:
      - manifest
      required: true
      docs:
      - id: domain.contract_set.id.doc.1
        summary: Contract export for `domain.contract_set.id`.
        audience: spec-authors
        status: active
        description: "Returns manifest `contract_set_id`.\n\nDocumentation metadata:\
          \ to description:\n- examples[]: title: Read id\ninput:\n  manifest:\n \
          \   contract_set_id: python_runner_contract_set\nexpected: python_runner_contract_set\\\
          \ n- params: - name: manifest\n  type: any\n  required: true\n  description:\
          \ Contract-set manifest object projection.\n- returns: type: string\ndescription:\
          \ Manifest contract-set identifier.\n- errors: - code: SCHEMA_ERROR\n  when:\
          \ Manifest does not contain the required field.\n  category: schema\n- portability:\
          \ python: true\nphp: true\nrust: true\nnotes: Portable stdlib projection."
        since: v1
    - as: domain.contract_set.depends_on
      from: assert.function
      path: /__export__domain.contract_set.depends_on
      params:
      - manifest
      required: true
      docs:
      - id: domain.contract_set.depends_on.doc.1
        summary: Contract export for `domain.contract_set.depends_on`.
        audience: spec-authors
        status: active
        description: "Returns declared dependency list from manifest.\\ n\nDocumentation\
          \ doc fields normalized to description:\n- examples[]: title: Read dependencies\n\
          input:\n  manifest:\n    depends_on:\n    - shared_makefile_help_contract_set\\\
          \ nexpected:\n- shared_makefile_help_contract_set\n- params: - name: manifest\n\
          \  type: any\n  required: true\n  description: Contract-set manifest object\
          \ projection.\n- returns: type: list\ndescription: Manifest dependency contract\
          \ set ids.\n- errors: - code: SCHEMA_ERROR\n  when: Manifest does not contain\
          \ the required field.\n  category: schema\n- portability: python: true\n\
          php: true\nrust: true\nnotes: Portable stdlib projection."
        since: v1
    - as: domain.contract_set.include_paths
      from: assert.function
      path: /__export__domain.contract_set.include_paths
      params:
      - manifest
      required: true
      docs:
      - id: domain.contract_set.include_paths.doc.1
        summary: Contract export for `domain.contract_set.include_paths`.
        audience: spec-authors
        status: active
        description: "Returns include path/glob list from manifest.\n\nDocumentation\
          \ fields normalized to description:\n- examples[]: title: Read include paths\n\
          input:\n  manifest:\n    include_paths:\n    - specs/impl/python/**\nexpected:\n\
          - specs/impl/python/**\n- params: - name: manifest\n  type: any\n  required:\
          \ true\n  description: Contract-set manifest object projection.\n- returns:\
          \ type: list\ndescription: Include path/glob list.\n- errors: - code: SCHEMA_ERROR\n\
          \  when: Manifest does not contain the required field.\n  category: schema\n\
          - portability: python: true\nphp: true\\ nrust: true\nnotes: Portable stdlib\
          \ projection."
        since: v1
    - as: domain.contract_set.applies_to_runners
      from: assert.function
      path: /__export__domain.contract_set.applies_to_runners
      params:
      - manifest
      required: true
      docs:
      - id: domain.contract_set.applies_to_runners.doc.1
        summary: Contract export for `domain.contract_set.applies_to_runners`.
        audience: spec-authors
        status: active
        description: "Returns optional runner applicability list.\n\nDocumentation metadata:\
          \ normalized to description:\\ n- examples[]: title: Read runner filter\n\
          input:\n  manifest:\n    applies_to_runners:\n    - python\n    - php\n\
          expected:\n- python\n- php\n- params: - name: manifest\n  type: any\n  required:\
          \ true\n  description: Contract-set manifest object projection.\n- returns:\
          \ type: list\ndescription: Runner ids list or null/empty list per manifest\
          \ authoring.\n- errors: - code: SCHEMA_ERROR\n  when: Manifest does not\
          \ contain expected structure.\n  category: schema\\ n- portability: python:\
          \ true\nphp: true\nrust: true\nnotes: Portable stdlib projection."
        since: v1
contracts:
  clauses:
  - id: LIB-DOMAIN-CONTRACT-SET-001
    title: contract-set manifest projection helper functions
    docs:
    - summary: Case `LIB-DOMAIN-CONTRACT-SET-001` for `contract.export`.
      audience: spec-authors
      status: active
      description: Contract-set manifest projection exports for resolver policy and
        validation checks.
      since: v1
      tags:
      - contract.export
    library:
      id: domain.contract_set.core
      module: domain
      stability: alpha
      owner: data-contracts
      tags:
      - domain
    asserts:
      checks:
      - id: __export__domain.contract_set.id
        assert:
          std.object.get:
          - var: manifest
          - contract_set_id
      - id: __export__domain.contract_set.depends_on
        assert:
          std.object.get:
          - var: manifest
          - depends_on
      - id: __export__domain.contract_set.include_paths
        assert:
          std.object.get:
          - var: manifest
          - include_paths
      - id: __export__domain.contract_set.applies_to_runners
        assert:
          std.object.get:
          - var: manifest
          - applies_to_runners
adapters:
- type: beta.exports_as_domain_contract_set_id_from_assert_function_path_export_domain_contract_set_id_params_manifest_required_true_docs_id_domain_contract_set_id_doc_1_summary_contract_export_for_domain_contract_set_id_audience_spec_authors_status_active_description_returns_manifest_contract_set_id_n_nprior_doc_fields_migrated_to_description_n_examples_title_read_id_ninput_n_manifest_n_contract_set_id_python_runner_contract_set_nexpected_python_runner_contract_set_n_params_name_manifest_n_type_any_n_required_true_n_description_contract_set_manifest_object_projection_n_returns_type_string_ndescription_manifest_contract_set_identifier_n_errors_code_schema_error_n_when_manifest_does_not_contain_the_required_field_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_portable_stdlib_projection_since_v1_as_domain_contract_set_depends_on_from_assert_function_path_export_domain_contract_set_depends_on_params_manifest_required_true_docs_id_domain_contract_set_depends_on_doc_1_summary_contract_export_for_domain_contract_set_depends_on_audience_spec_authors_status_active_description_returns_declared_dependency_list_from_manifest_n_nprior_doc_fields_migrated_to_description_n_examples_title_read_dependencies_ninput_n_manifest_n_depends_on_n_shared_makefile_help_contract_set_nexpected_n_shared_makefile_help_contract_set_n_params_name_manifest_n_type_any_n_required_true_n_description_contract_set_manifest_object_projection_n_returns_type_list_ndescription_manifest_dependency_contract_set_ids_n_errors_code_schema_error_n_when_manifest_does_not_contain_the_required_field_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_portable_stdlib_projection_since_v1_as_domain_contract_set_include_paths_from_assert_function_path_export_domain_contract_set_include_paths_params_manifest_required_true_docs_id_domain_contract_set_include_paths_doc_1_summary_contract_export_for_domain_contract_set_include_paths_audience_spec_authors_status_active_description_returns_include_path_glob_list_from_manifest_n_nprior_doc_fields_migrated_to_description_n_examples_title_read_include_paths_ninput_n_manifest_n_include_paths_n_specs_impl_python_nexpected_n_specs_impl_python_n_params_name_manifest_n_type_any_n_required_true_n_description_contract_set_manifest_object_projection_n_returns_type_list_ndescription_include_path_glob_list_n_errors_code_schema_error_n_when_manifest_does_not_contain_the_required_field_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_portable_stdlib_projection_since_v1_as_domain_contract_set_applies_to_runners_from_assert_function_path_export_domain_contract_set_applies_to_runners_params_manifest_required_true_docs_id_domain_contract_set_applies_to_runners_doc_1_summary_contract_export_for_domain_contract_set_applies_to_runners_audience_spec_authors_status_active_description_returns_optional_runner_applicability_list_n_nprior_doc_fields_migrated_to_description_n_examples_title_read_runner_filter_ninput_n_manifest_n_applies_to_runners_n_python_n_php_nexpected_n_python_n_php_n_params_name_manifest_n_type_any_n_required_true_n_description_contract_set_manifest_object_projection_n_returns_type_list_ndescription_runner_ids_list_or_null_empty_list_per_manifest_authoring_n_errors_code_schema_error_n_when_manifest_does_not_contain_expected_structure_n_category_schema_n_portability_python_true_nphp_true_nrust_true_nnotes_portable_stdlib_projection_since_v1
  actions:
  - id: act.lib.contract.set.core.spec.1
    direction: bidirectional
    profile: default
services:
- id: svc.lib.contract.set.core.spec.1
  consumes:
  - act.lib.contract.set.core.spec.1
```
