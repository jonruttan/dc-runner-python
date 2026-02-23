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
    - ref: '#LIB-POLICY-SCHEMA-PIN-001'
      as: lib_policy_schema_pin
      symbols:
      - policy.schema_pin.missing_spec_version_zero
      - policy.schema_pin.missing_schema_ref_zero
      - policy.schema_pin.unknown_schema_ref_zero
      - policy.schema_pin.version_match_zero
    exports:
    - as: policy.schema_pin.missing_spec_version_zero
      from: assert.function
      path: /__export__policy.schema_pin.missing_spec_version_zero
      params:
      - subject
      required: true
    - as: policy.schema_pin.missing_schema_ref_zero
      from: assert.function
      path: /__export__policy.schema_pin.missing_schema_ref_zero
      params:
      - subject
      required: true
    - as: policy.schema_pin.unknown_schema_ref_zero
      from: assert.function
      path: /__export__policy.schema_pin.unknown_schema_ref_zero
      params:
      - subject
      required: true
    - as: policy.schema_pin.version_match_zero
      from: assert.function
      path: /__export__policy.schema_pin.version_match_zero
      params:
      - subject
      required: true
contracts:
  clauses:
  - id: LIB-POLICY-SCHEMA-PIN-001
    title: schema pin extractor predicates
    library:
      id: policy.schema.pin
      module: policy
      stability: alpha
      owner: data-contracts
      tags:
      - policy
      - schema
    type: contract.export
    asserts:
      checks:
      - id: __export__policy.schema_pin.missing_spec_version_zero
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - missing_spec_version_count
          - 0
      - id: __export__policy.schema_pin.missing_schema_ref_zero
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - missing_schema_ref_count
          - 0
      - id: __export__policy.schema_pin.unknown_schema_ref_zero
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - unknown_schema_ref_count
          - 0
      - id: __export__policy.schema_pin.version_match_zero
        assert:
          std.logic.eq:
          - std.object.get:
            - var: subject
            - mismatched_version_count
          - 0
  - id: LIB-POLICY-SCHEMA-PIN-900
    title: schema pin policy library smoke
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
          - var: policy.schema_pin.missing_spec_version_zero
          - lit:
              missing_spec_version_count: 0
        - call:
          - var: policy.schema_pin.missing_schema_ref_zero
          - lit:
              missing_schema_ref_count: 0
        - call:
          - var: policy.schema_pin.unknown_schema_ref_zero
          - lit:
              unknown_schema_ref_count: 0
        - call:
          - var: policy.schema_pin.version_match_zero
          - lit:
              mismatched_version_count: 0
adapters:
- type: beta.exports_as_policy_schema_pin_missing_spec_version_zero_from_assert_function_path_export_policy_schema_pin_missing_spec_version_zero_params_subject_required_true_as_policy_schema_pin_missing_schema_ref_zero_from_assert_function_path_export_policy_schema_pin_missing_schema_ref_zero_params_subject_required_true_as_policy_schema_pin_unknown_schema_ref_zero_from_assert_function_path_export_policy_schema_pin_unknown_schema_ref_zero_params_subject_required_true_as_policy_schema_pin_version_match_zero_from_assert_function_path_export_policy_schema_pin_version_match_zero_params_subject_required_true
  actions:
  - id: act.lib.policy.schema.pin.spec.1
    profile: default
- type: beta.check_profile_text_file_config_use_ref_lib_policy_schema_pin_001_as_lib_policy_schema_pin_symbols_policy_schema_pin_missing_spec_version_zero_policy_schema_pin_missing_schema_ref_zero_policy_schema_pin_unknown_schema_ref_zero_policy_schema_pin_version_match_zero
  actions:
  - id: act.lib.policy.schema.pin.spec.2
    profile: default
services:
- id: svc.lib.policy.schema.pin.spec.1
  consumes:
  - act.lib.policy.schema.pin.spec.1
- id: svc.lib.policy.schema.pin.spec.2
  consumes:
  - act.lib.policy.schema.pin.spec.2
```


