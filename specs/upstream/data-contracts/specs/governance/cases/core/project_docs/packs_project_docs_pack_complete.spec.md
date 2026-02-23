```yaml contract-spec
id: DCGOV-PACK-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: project-docs maintenance pack is complete
purpose: Ensures docs maintenance pack includes README/book coherence surfaces.
type: contract.check
harness:
  root: .
  pack:
    path: /specs/packs/project_docs_maintenance_pack_v1.yaml
    required_tokens:
      - pack_id: project_docs_maintenance_pack_v1
      - /specs/02_contracts/10_docs_quality.md
      - /specs/governance/cases/core/project_docs/docs_readme_task_usage_paths_present.spec.md
  check:
    profile: governance.scan
    config:
      check: packs.project_docs_pack_complete
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names: [violation_count]
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
```
