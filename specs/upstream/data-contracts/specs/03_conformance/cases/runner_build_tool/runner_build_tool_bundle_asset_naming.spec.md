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
        path: /specs/02_contracts/33_bundle_package_management.md
contracts:
  clauses:
  - id: DCCONF-BTOOL-006
    title: bundle package contract defines canonical data-contract-bundle asset naming
    purpose: Ensures bundle package contract uses the canonical data-contract-bundle
      prefix and version token format.
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
          - data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz.sha256
      - id: assert_3
        assert:
          std.string.contains:
          - var: text
          - data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz.intoto.json
      - id: assert_4
        assert:
          std.logic.not:
            std.string.contains:
            - var: text
            - bundle-{bundle_id}-{bundle_version}.tar.gz
adapters:
- type: beta.check_profile_text_file_config_path_specs_contract_33_bundle_package_management_md
  actions:
  - id: act.conf.runner.build.tool.bundle.1
    direction: bidirectional
    profile: default
services:
- id: svc.conf.runner.build.tool.bundle.1
  consumes:
  - act.conf.runner.build.tool.bundle.1
```
