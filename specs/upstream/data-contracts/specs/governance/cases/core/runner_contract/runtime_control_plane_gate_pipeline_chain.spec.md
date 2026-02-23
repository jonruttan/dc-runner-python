```yaml contract-spec
id: DCGOV-PIPE-GATE-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: control-plane gate pipeline is chained
purpose: Ensures governance, docs, and ingest gates are chained and enforced through contract checks.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.control_plane_gate_chain_valid
  chain:
    fail_fast: true
    steps:
      - id: step_catalog_pipeline
        class: must
        ref: /specs/governance/cases/core/spec_core/runtime_governance_catalog_pipeline_chain.spec.md#DCGOV-PIPE-CATALOG-001
      - id: step_schema_pipeline
        class: must
        ref: /specs/governance/cases/core/spec_core/runtime_schema_pin_pipeline_chain.spec.md#DCGOV-PIPE-SCHEMA-001
      - id: step_ingest_pipeline
        class: must
        ref: /specs/governance/cases/core/runner_contract/runtime_status_ingest_pipeline_chain.spec.md#DCGOV-PIPE-INGEST-001
      - id: step_optional_pipeline
        class: can
        ref: /specs/governance/cases/core/runtime_optional_report_pipeline_chain.spec.md#DCGOV-PIPE-OPTIONAL-001
  use:
    - ref: /specs/05_libraries/policy/policy_ci_gate.spec.md#LIB-POLICY-CI-001
      as: lib_policy_ci
      symbols:
        - policy.ci.required_profiles_pass
        - policy.ci.optional_profile_report_only
        - policy.ci.artifacts_present
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
            - {var: policy.ci.required_profiles_pass}
            - std.object.get:
                - {var: context_json}
                - ci_gate_summary
        - call:
            - {var: policy.ci.artifacts_present}
            - std.object.get:
                - {var: context_json}
                - ci_gate_summary
```
