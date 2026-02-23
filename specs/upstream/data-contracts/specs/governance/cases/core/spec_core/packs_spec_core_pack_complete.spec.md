```yaml contract-spec
id: DCGOV-PACK-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec-core maintenance pack is complete
purpose: Ensures spec-core pack includes schema and governance maintenance surfaces.
type: contract.check
harness:
  root: .
  pack:
    path: /specs/packs/spec_core_maintenance_pack_v1.yaml
    required_tokens:
      - pack_id: spec_core_maintenance_pack_v1
      - /specs/01_schema/schema_v1.md
      - /specs/01_schema/schema_catalog_v1.yaml
      - /specs/governance/cases/core/spec_core/runtime_schema_pin_pipeline_chain.spec.md
  check:
    profile: governance.scan
    config:
      check: packs.spec_core_pack_complete
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
