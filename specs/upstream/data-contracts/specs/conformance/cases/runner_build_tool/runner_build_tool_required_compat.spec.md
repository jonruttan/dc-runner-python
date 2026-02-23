```yaml contract-spec
id: DCCONF-BTOOL-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner build tool contract defines required compat task
purpose: Portable build tool contract must define compat-check required task.
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
          - compat-check
```
