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
        path: /scripts/bundle
contracts:
  clauses:
  - id: DCCONF-BTOOL-007
    title: bundle tooling exposes install command surface
    purpose: Bundle CLI must expose install and install-check commands for multi-bundle
      project workflows.
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
          - scripts/bundle install --project-lock
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - scripts/bundle install-check --project-lock
adapters:
- type: beta.check_profile_text_file_config_path_scripts_bundle
  actions:
  - id: act.conf.runner.build.tool.instal.1
    direction: bidirectional
    profile: default
services:
- id: svc.conf.runner.build.tool.instal.1
  consumes:
  - act.conf.runner.build.tool.instal.1
```
