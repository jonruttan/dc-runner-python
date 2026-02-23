```yaml contract-spec
id: DCGOV-RUNTIME-BTOOL-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner build tool contract document is defined
purpose: Ensures tool-agnostic build tool contract document is present in the portable contract index.
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
          - /specs/02_contracts/30_build_tool_command_set.md
```
