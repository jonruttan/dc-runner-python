```yaml contract-spec
id: DCGOV-PIPE-SCHEMA-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: schema pin pipeline is chained and policy-backed
purpose: Ensures schema pin checks are linked as a chain and validated through policy library exports.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.pin_pipeline_chain_valid
  chain:
    fail_fast: true
    steps:
      - id: step_spec_version_present
        class: must
        ref: /specs/governance/cases/core/spec_core/schema_spec_case_version_present.spec.md#DCGOV-SCHEMA-PIN-001
      - id: step_schema_ref_present
        class: must
        ref: /specs/governance/cases/core/spec_core/schema_spec_case_schema_ref_present.spec.md#DCGOV-SCHEMA-PIN-002
      - id: step_schema_ref_known
        class: must
        ref: /specs/governance/cases/core/spec_core/schema_spec_case_schema_ref_known.spec.md#DCGOV-SCHEMA-PIN-003
      - id: step_version_match
        class: must
        ref: /specs/governance/cases/core/spec_core/schema_spec_case_version_matches_schema_ref.spec.md#DCGOV-SCHEMA-PIN-004
  use:
    - ref: /specs/05_libraries/policy/policy_schema_pin.spec.md#LIB-POLICY-SCHEMA-PIN-001
      as: lib_policy_schema_pin
      symbols:
        - policy.schema_pin.missing_spec_version_zero
        - policy.schema_pin.missing_schema_ref_zero
        - policy.schema_pin.unknown_schema_ref_zero
        - policy.schema_pin.version_match_zero
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names:
        - violation_count
        - context_json
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
    - id: assert_2
      assert:
        - call:
            - {var: policy.schema_pin.missing_spec_version_zero}
            - std.object.get:
                - {var: context_json}
                - spec_schema_pin_validate
        - call:
            - {var: policy.schema_pin.missing_schema_ref_zero}
            - std.object.get:
                - {var: context_json}
                - spec_schema_pin_validate
        - call:
            - {var: policy.schema_pin.unknown_schema_ref_zero}
            - std.object.get:
                - {var: context_json}
                - spec_schema_pin_validate
        - call:
            - {var: policy.schema_pin.version_match_zero}
            - std.object.get:
                - {var: context_json}
                - spec_schema_pin_validate
```
