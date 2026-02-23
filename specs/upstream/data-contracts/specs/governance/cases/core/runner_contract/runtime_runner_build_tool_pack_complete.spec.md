```yaml contract-spec
id: DCGOV-RUNTIME-BTOOL-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner contract pack includes build tool contract surface
purpose: Ensures runner contract pack includes build tool contract and conformance case coverage.
type: contract.check
harness:
  root: .
  pack:
    path: /specs/packs/runner_contract_pack_v1.yaml
    required_tokens:
      - /specs/02_contracts/30_build_tool_command_set.md
      - /specs/01_schema/runner_build_tool_contract_v1.yaml
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_required_core.spec.md
  check:
    profile: governance.scan
    config:
      check: packs.runner_contract_pack_complete
contract:
  defaults:
    class: SHOULD
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
