```yaml contract-spec
id: DCCONF-RCLI-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner cli supports optional capability negotiation
purpose: Portable CLI contract allows optional capability flags such as structured output mode.
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
      class: MAY
      assert:
        std.string.contains:
          - {var: text}
          - --json
```
