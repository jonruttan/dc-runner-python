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
        path: /specs/01_schema/project_bundle_lock_v1.yaml
contracts:
  clauses:
  - id: DCCONF-BTOOL-011
    title: project bundle lock schema supports additional role entries
    purpose: Project lock schema must allow role additional for implementation-specific
      bundles.
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
          - role
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - primary
      - id: assert_3
        assert:
          std.string.contains:
          - var: text
          - additional
adapters:
- type: beta.check_profile_text_file_config_path_specs_schema_project_bundle_lock_v1_yaml
  actions:
  - id: act.conf.runner.build.tool.projec.1
    direction: bidirectional
    profile: default
services:
- id: svc.conf.runner.build.tool.projec.1
  consumes:
  - act.conf.runner.build.tool.projec.1
```
