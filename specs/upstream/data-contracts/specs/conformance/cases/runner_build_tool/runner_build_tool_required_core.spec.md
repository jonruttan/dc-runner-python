```yaml contract-spec
id: DCCONF-BTOOL-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner build tool contract defines required core tasks
purpose: Portable build tool contract must define build, test, and verify required tasks.
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
          - build
    - id: assert_2
      assert:
        std.string.contains:
          - {var: text}
          - test
    - id: assert_3
      assert:
        std.string.contains:
          - {var: text}
          - verify
```
