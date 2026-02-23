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
  - id: DCCONF-BTOOL-005
    title: runner build tool contract declares manifest path requirement
    purpose: Build tool command contract must require each runner repository to publish
      a task map manifest path.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: text
          - /data-contracts-library/specs/07_runner_behavior/impl/<runner>/runner_build_tool_contract_v1.yaml
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
