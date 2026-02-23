```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PIPE-GATE-001
    title: control-plane gate pipeline is chained
    purpose: Ensures governance, docs, and ingest gates are chained and enforced through contract checks.
    harness:
      root: "."
      check:
        profile: governance.scan
        config:
          check: runtime.control_plane_gate_chain_valid
      chain:
        fail_fast: true
        steps:
        - id: step_catalog_pipeline
          required: true
          ref: "/specs/04_governance/cases/core/spec_core/runtime_governance_catalog_pipeline_chain.spec.md#DCGOV-PIPE-CATALOG-001"
        - id: step_schema_pipeline
          required: true
          ref: "/specs/04_governance/cases/core/spec_core/runtime_schema_pin_pipeline_chain.spec.md#DCGOV-PIPE-SCHEMA-001"
        - id: step_ingest_pipeline
          required: true
          ref: "/specs/04_governance/cases/core/runner_contract/runtime_status_ingest_pipeline_chain.spec.md#DCGOV-PIPE-INGEST-001"
        - id: step_optional_pipeline
          required: false
          ref: "/specs/04_governance/cases/core/runtime_optional_report_pipeline_chain.spec.md#DCGOV-PIPE-OPTIONAL-001"
      use:
      - ref: "/specs/05_libraries/policy/policy_ci_gate.spec.md#LIB-POLICY-CI-001"
        as: lib_policy_ci
        symbols:
        - policy.ci.required_profiles_pass
        - policy.ci.optional_profile_report_only
        - policy.ci.artifacts_present
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
          - var: policy.ci.required_profiles_pass
          - std.object.get:
            - var: context_json
            - ci_gate_summary
        - call:
          - var: policy.ci.artifacts_present
          - std.object.get:
            - var: context_json
            - ci_gate_summary
```
