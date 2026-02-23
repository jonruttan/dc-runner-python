```yaml contract-spec
id: DCGOV-PACK-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: pack paths resolve in repository
purpose: Ensures all pack manifests and referenced case paths exist.
type: contract.check
harness:
  root: .
  required_paths:
    - /specs/packs/runner_contract_pack_v1.yaml
    - /specs/packs/spec_core_maintenance_pack_v1.yaml
    - /specs/packs/project_docs_maintenance_pack_v1.yaml
    - /specs/03_conformance/cases/runner_cli/runner_cli_required_help.spec.md
    - /specs/03_conformance/cases/runner_cli/runner_cli_required_governance.spec.md
    - /specs/03_conformance/cases/runner_cli/runner_cli_required_conformance.spec.md
    - /specs/03_conformance/cases/runner_cli/runner_cli_unknown_command.spec.md
    - /specs/03_conformance/cases/runner_cli/runner_cli_optional_capability_negotiation.spec.md
  check:
    profile: governance.scan
    config:
      check: packs.pack_paths_resolve
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
