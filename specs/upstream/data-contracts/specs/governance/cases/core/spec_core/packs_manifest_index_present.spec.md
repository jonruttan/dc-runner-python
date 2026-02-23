```yaml contract-spec
id: DCGOV-PACK-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: packs index manifest exists
purpose: Ensures spec pack index is present and discoverable.
type: contract.check
harness:
  root: .
  packs_index:
    path: /specs/packs/index.md
    required_tokens:
      - /specs/packs/runner_contract_pack_v1.yaml
      - /specs/packs/spec_core_maintenance_pack_v1.yaml
      - /specs/packs/project_docs_maintenance_pack_v1.yaml
  check:
    profile: governance.scan
    config:
      check: packs.manifest_index_present
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
