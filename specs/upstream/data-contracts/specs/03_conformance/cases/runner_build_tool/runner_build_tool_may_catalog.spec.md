```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    check:
      profile: text.file
      config: {}
contracts:
  clauses:
  - id: DCCONF-BTOOL-004
    title: runner build tool contract defines optional task catalog
    purpose: Portable build tool contract should declare the MAY task catalog for
      optional capabilities.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        required: false
        assert:
          std.string.contains:
          - var: text
          - smoke
      - id: assert_2
        required: false
        assert:
          std.string.contains:
          - var: text
          - package-check
      - id: assert_3
        required: false
        assert:
          std.string.contains:
          - var: text
          - release-verify
      - id: assert_4
        required: false
        assert:
          std.string.contains:
          - var: text
          - docs-check
      - id: assert_5
        required: false
        assert:
          std.string.contains:
          - var: text
          - lint
      - id: assert_6
        required: false
        assert:
          std.string.contains:
          - var: text
          - typecheck
adapters:
- type: beta.check_profile_text_file_config
  actions:
  - id: svc.check_profile_text_file_config.default.1
    direction: bidirectional
    profile: default
services:
- id: svc.check_profile_text_file_config.default.1
  consumes:
  - svc.check_profile_text_file_config.default.1
```
