```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PIPE-LIB-001
    title: policy library exports resolve for pipelines
    purpose: Ensures policy symbol libraries for pipeline checks are present and loadable.
    harness:
      root: "."
      use:
      - ref: "/specs/05_libraries/policy/policy_governance_catalog.spec.md#LIB-POLICY-GOV-CATALOG-001"
        as: lib_policy_catalog
        symbols:
        - policy.catalog.duplicate_ids_zero
      - ref: "/specs/05_libraries/policy/policy_schema_pin.spec.md#LIB-POLICY-SCHEMA-PIN-001"
        as: lib_policy_schema
        symbols:
        - policy.schema_pin.version_match_zero
      - ref: "/specs/05_libraries/policy/policy_status_ingest.spec.md#LIB-POLICY-INGEST-001"
        as: lib_policy_ingest
        symbols:
        - policy.ingest.matrix_has_rows
      - ref: "/specs/05_libraries/policy/policy_ci_gate.spec.md#LIB-POLICY-CI-001"
        as: lib_policy_ci
        symbols:
        - policy.ci.required_profiles_pass
      check:
        profile: governance.scan
        config:
          check: runtime.policy_library_exports_resolve
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
