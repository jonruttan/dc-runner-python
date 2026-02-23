```yaml contract-spec
id: DCCONF-RCLI-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner cli exposes help command
purpose: Portable CLI contract requires help surface.
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
          - runner --help
```
