```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PIPE-CHAIN-001
    title: chain entry cases exist for script domains
    purpose: Ensures all required chain pipeline case files are present.
    harness:
      root: "."
      required_chain_cases:
        paths:
        - "/specs/04_governance/cases/core/spec_core/runtime_governance_catalog_pipeline_chain.spec.md"
        - "/specs/04_governance/cases/core/spec_core/runtime_schema_pin_pipeline_chain.spec.md"
        - "/specs/04_governance/cases/core/runtime_optional_report_pipeline_chain.spec.md"
        - "/specs/04_governance/cases/core/runner_contract/runtime_status_ingest_pipeline_chain.spec.md"
        - "/specs/04_governance/cases/core/runner_contract/runtime_control_plane_gate_pipeline_chain.spec.md"
      check:
        profile: governance.scan
        config:
          check: runtime.chain_entry_cases_present
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
```
