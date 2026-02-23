```yaml contract-spec
id: DCGOV-PACK-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner contract pack is complete
purpose: Ensures runner-contract pack includes CLI and status exchange surfaces.
type: contract.check
harness:
  root: .
  pack:
    path: /specs/packs/runner_contract_pack_v1.yaml
    required_tokens:
      - pack_id: runner_contract_pack_v1
      - /specs/02_contracts/29_runner_cli_interface.md
      - /specs/02_contracts/30_build_tool_command_set.md
      - /specs/01_schema/runner_cli_contract_v1.yaml
      - /specs/01_schema/runner_build_tool_contract_v1.yaml
      - /specs/03_conformance/cases/runner_cli/runner_cli_required_help.spec.md
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_required_core.spec.md
  check:
    profile: governance.scan
    config:
      check: packs.runner_contract_pack_complete
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
