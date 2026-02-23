```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PACK-004
    title: project-docs maintenance pack is complete
    purpose: Ensures docs maintenance pack includes README/book coherence surfaces.
    harness:
      root: "."
      pack:
        path: "/specs/00_core/packs/project_docs_maintenance_pack_v1.yaml"
        required_tokens:
        - pack_id: project_docs_maintenance_pack_v1
        - "/specs/02_contracts/10_docs_quality.md"
        - "/specs/04_governance/cases/core/project_docs/docs_readme_task_usage_paths_present.spec.md"
      check:
        profile: governance.scan
        config:
          check: packs.project_docs_pack_complete
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
