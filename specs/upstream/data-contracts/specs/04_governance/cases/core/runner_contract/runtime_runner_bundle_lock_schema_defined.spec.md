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
        path: /specs/01_schema/index.md
contracts:
  clauses:
  - id: DCGOV-RUNTIME-BUNDLE-002
    title: project bundle lock schema is indexed
    purpose: Ensures schema index includes project bundle lock schema for multi-bundle
      installs.
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
          - /specs/01_schema/bundle_manifest_v1.yaml
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - /specs/01_schema/resolved_bundle_lock_v1.yaml
      - id: assert_3
        assert:
          std.string.contains:
          - var: text
          - /specs/01_schema/project_bundle_lock_v1.yaml
adapters:
- type: beta.check_profile_text_file_config_path_specs_schema_index_md
  actions:
  - id: act.gov.runtime.runner.bundle.lo.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.runner.bundle.lo.1
  consumes:
  - act.gov.runtime.runner.bundle.lo.1
```
