```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    check:
      profile: text.file
      config:
        path: /specs/02_contracts/30_build_tool_command_set.md
contracts:
  clauses:
  - id: DCCONF-BTOOL-002
    title: runner build tool contract defines required bundle sync tasks
    purpose: Portable build tool contract must define bundle-sync and bundle-sync-check
      required tasks.
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
          - bundle-sync
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - bundle-sync-check
      - id: assert_3
        assert:
          std.logic.not:
            std.string.contains:
            - var: text
            - '`spec-sync`'
      - id: assert_4
        assert:
          std.logic.not:
            std.string.contains:
            - var: text
            - '`spec-sync-check`'
adapters:
- type: beta.check_profile_text_file_config_path_specs_contract_30_build_tool_command_set_md
  actions:
  - id: act.conf.runner.build.tool.requir.1
    direction: bidirectional
    profile: default
services:
- id: svc.conf.runner.build.tool.requir.1
  consumes:
  - act.conf.runner.build.tool.requir.1
```
