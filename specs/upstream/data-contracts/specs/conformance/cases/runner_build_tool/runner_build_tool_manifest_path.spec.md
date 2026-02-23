```yaml contract-spec
id: DCCONF-BTOOL-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner build tool contract declares manifest path requirement
purpose: Build tool command contract must require each runner repository to publish a task map manifest path.
type: contract.check
harness:
  check:
    profile: text.file
    config: {}
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names: [text]
  steps:
    - id: assert_1
      assert:
        std.string.contains:
          - {var: text}
          - /specs/impl/<runner>/runner_build_tool_contract_v1.yaml
```
