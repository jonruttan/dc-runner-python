```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PACK-001
    title: packs index manifest exists
    purpose: Ensures spec pack index is present and discoverable.
    harness:
      root: "."
      packs_index:
        path: "/specs/00_core/packs/index.md"
        required_tokens:
        - "/specs/00_core/packs/runner_contract_pack_v1.yaml"
        - "/specs/00_core/packs/spec_core_maintenance_pack_v1.yaml"
        - "/specs/00_core/packs/project_docs_maintenance_pack_v1.yaml"
      check:
        profile: governance.scan
        config:
          check: packs.manifest_index_present
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
