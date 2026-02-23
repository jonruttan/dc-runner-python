```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PIPE-CATALOG-001
    title: governance catalog pipeline is chained and policy-backed
    purpose: Ensures governance catalog policy checks are composed through harness.chain and validated by reusable policy predicates.
    harness:
      root: "."
      check:
        profile: governance.scan
        config:
          check: governance.catalog_pipeline_chain_valid
      chain:
        fail_fast: true
        steps:
        - id: step_catalog_shape
          required: true
          ref: "/specs/04_governance/cases/core/runtime_artifact_contract_compatibility_preserved.spec.md#DCGOV-RUNTIME-SHELL-002"
        - id: step_duplicate_ids
          required: true
          ref: "/specs/04_governance/cases/core/spec_core/governance_policy_source_spec_lang_required.spec.md#DCGOV-POLICY-SRC-001"
        - id: step_unmapped
          required: true
          ref: "/specs/04_governance/cases/core/runner_contract/runtime_shell_policy_branches_forbidden.spec.md#DCGOV-RUNTIME-SHELL-001"
        - id: step_tier_collision
          required: true
          ref: "/specs/04_governance/cases/core/runtime_infra_script_boundary_enforced.spec.md#DCGOV-RUNTIME-SHELL-003"
      use:
      - ref: "/specs/05_libraries/policy/policy_governance_catalog.spec.md#LIB-POLICY-GOV-CATALOG-001"
        as: lib_policy_catalog
        symbols:
        - policy.catalog.duplicate_ids_zero
        - policy.catalog.unmapped_checks_zero
        - policy.catalog.multi_tier_collisions_zero
        - policy.catalog.check_field_presence_zero
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
        - context_json
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
      - id: assert_2
        assert:
        - call:
          - var: policy.catalog.duplicate_ids_zero
          - std.object.get:
            - var: context_json
            - governance_catalog_validate
        - call:
          - var: policy.catalog.unmapped_checks_zero
          - std.object.get:
            - var: context_json
            - governance_catalog_validate
        - call:
          - var: policy.catalog.multi_tier_collisions_zero
          - std.object.get:
            - var: context_json
            - governance_catalog_validate
        - call:
          - var: policy.catalog.check_field_presence_zero
          - std.object.get:
            - var: context_json
            - governance_catalog_validate
```
