```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PACK-003
    title: spec-core maintenance pack is complete
    purpose: Ensures spec-core pack includes schema and governance maintenance surfaces.
    harness:
      root: "."
      pack:
        path: "/specs/00_core/packs/spec_core_maintenance_pack_v1.yaml"
        required_tokens:
        - pack_id: spec_core_maintenance_pack_v1
        - "/specs/01_schema/schema_v1.md"
        - "/specs/01_schema/schema_catalog_v1.yaml"
        - "/specs/04_governance/cases/core/spec_core/runtime_schema_pin_pipeline_chain.spec.md"
      check:
        profile: governance.scan
        config:
          check: packs.spec_core_pack_complete
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
