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
    - ref: '#LIB-POLICY-GOV-CATALOG-001'
      as: lib_policy_gov_catalog
      symbols:
      - policy.catalog.duplicate_ids_zero
      - policy.catalog.unmapped_checks_zero
      - policy.catalog.multi_tier_collisions_zero
      - policy.catalog.check_field_presence_zero
    exports:
    - as: policy.catalog.duplicate_ids_zero
      from: assert.function
      path: /__export__policy.catalog.duplicate_ids_zero
      params:
      - subject
      required: true
    - as: policy.catalog.unmapped_checks_zero
      from: assert.function
      path: /__export__policy.catalog.unmapped_checks_zero
      params:
      - subject
      required: true
    - as: policy.catalog.multi_tier_collisions_zero
      from: assert.function
      path: /__export__policy.catalog.multi_tier_collisions_zero
      params:
      - subject
      required: true
    - as: policy.catalog.check_field_presence_zero
      from: assert.function
      path: /__export__policy.catalog.check_field_presence_zero
      params:
      - subject
      required: true
contracts:
  clauses:
  - id: LIB-POLICY-GOV-CATALOG-001
    title: governance catalog extractor predicates
    library:
      id: policy.governance.catalog
      module: policy
      stability: alpha
      owner: data-contracts
      tags:
      - policy
      - governance
    type: contract.export
    asserts:
      checks:
      - id: __export__policy.catalog.duplicate_ids_zero
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - duplicate_case_id_count
          - 0
      - id: __export__policy.catalog.unmapped_checks_zero
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - unmapped_case_check_count
          - 0
      - id: __export__policy.catalog.multi_tier_collisions_zero
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - multi_tier_case_check_count
          - 0
      - id: __export__policy.catalog.check_field_presence_zero
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - missing_case_check_field_count
          - 0
  - id: LIB-POLICY-GOV-CATALOG-900
    title: governance catalog policy library smoke
    type: contract.check
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.catalog.duplicate_ids_zero
          - lit:
              duplicate_case_id_count: 0
        - call:
          - var: policy.catalog.unmapped_checks_zero
          - lit:
              unmapped_case_check_count: 0
        - call:
          - var: policy.catalog.multi_tier_collisions_zero
          - lit:
              multi_tier_case_check_count: 0
        - call:
          - var: policy.catalog.check_field_presence_zero
          - lit:
              missing_case_check_field_count: 0
adapters:
- type: beta.exports_as_policy_catalog_duplicate_ids_zero_from_assert_function_path_export_policy_catalog_duplicate_ids_zero_params_subject_required_true_as_policy_catalog_unmapped_checks_zero_from_assert_function_path_export_policy_catalog_unmapped_checks_zero_params_subject_required_true_as_policy_catalog_multi_tier_collisions_zero_from_assert_function_path_export_policy_catalog_multi_tier_collisions_zero_params_subject_required_true_as_policy_catalog_check_field_presence_zero_from_assert_function_path_export_policy_catalog_check_field_presence_zero_params_subject_required_true
  actions:
  - id: act.lib.policy.governance.catalo.1
    profile: default
- type: beta.check_profile_text_file_config_use_ref_lib_policy_gov_catalog_001_as_lib_policy_gov_catalog_symbols_policy_catalog_duplicate_ids_zero_policy_catalog_unmapped_checks_zero_policy_catalog_multi_tier_collisions_zero_policy_catalog_check_field_presence_zero
  actions:
  - id: act.lib.policy.governance.catalo.2
    profile: default
services:
- id: svc.lib.policy.governance.catalo.1
  consumes:
  - act.lib.policy.governance.catalo.1
- id: svc.lib.policy.governance.catalo.2
  consumes:
  - act.lib.policy.governance.catalo.2
```


