```yaml contract-spec
id: DCCONF-BTOOL-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner build tool contract defines optional task catalog
purpose: Portable build tool contract should declare the MAY task catalog for optional capabilities.
type: contract.check
harness:
  check:
    profile: text.file
    config: {}
contract:
  defaults:
    class: SHOULD
  imports:
    - from: artifact
      names: [text]
  steps:
    - id: assert_1
      assert:
        std.string.contains:
          - {var: text}
          - smoke
    - id: assert_2
      assert:
        std.string.contains:
          - {var: text}
          - package-check
    - id: assert_3
      assert:
        std.string.contains:
          - {var: text}
          - release-verify
    - id: assert_4
      assert:
        std.string.contains:
          - {var: text}
          - docs-check
    - id: assert_5
      assert:
        std.string.contains:
          - {var: text}
          - lint
    - id: assert_6
      assert:
        std.string.contains:
          - {var: text}
          - typecheck
```
