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
        path: /specs/01_schema/implementation_bundle_overlay_v1.yaml
contracts:
  clauses:
  - id: DCCONF-BTOOL-009
    title: implementation overlay schema defines patch overlay fields
    purpose: Implementation overlay schema must define add/replace/delete patch surfaces
      and output bundle metadata.
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
          - add_files
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - replace_files
      - id: assert_3
        assert:
          std.string.contains:
          - var: text
          - delete_paths
      - id: assert_4
        assert:
          std.string.contains:
          - var: text
          - output_bundle
adapters:
- type: beta.check_profile_text_file_config_path_specs_schema_implementation_bundle_overlay_v1_yaml
  actions:
  - id: act.conf.runner.build.tool.impl.o.1
    direction: bidirectional
    profile: default
services:
- id: svc.conf.runner.build.tool.impl.o.1
  consumes:
  - act.conf.runner.build.tool.impl.o.1
```
