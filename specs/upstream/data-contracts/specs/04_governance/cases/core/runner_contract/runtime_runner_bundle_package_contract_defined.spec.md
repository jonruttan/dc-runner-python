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
        path: /specs/01_schema/runner_build_tool_contract_v1.yaml
contracts:
  clauses:
  - id: DCGOV-RUNTIME-BUNDLE-001
    title: runner bundle package management contract is defined
    purpose: Ensures bundle package management contract describes release-asset and
      checksum requirements.
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
          std.string.contains:
          - var: text
          - release-asset
      - id: assert_4
        assert:
          std.string.contains:
          - var: text
          - checksum
      - id: assert_5
        assert:
          std.string.contains:
          - var: text
          - bundles.lock.yaml
      - id: assert_6
        assert:
          std.string.contains:
          - var: text
          - data-contracts-bundles
      - id: assert_7
        assert:
          std.string.contains:
          - var: text
          - data-contracts-library
  - id: DCGOV-RUNTIME-BUNDLE-003
    title: runner build tool schema declares bundle sync tasks
    purpose: Ensures runner build tool schema uses bundle-sync task ids and does not
      include canonical spec-sync task ids.
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
            - spec-sync
adapters:
- type: beta.check_profile_text_file_config_path_specs_contract_33_bundle_package_management_md
  actions:
  - id: act.gov.runtime.runner.bundle.pa.1
    profile: default
- type: beta.check_profile_text_file_config_path_specs_schema_runner_build_tool_contract_v1_yaml
  actions:
  - id: act.gov.runtime.runner.bundle.pa.2
    profile: default
services:
- id: svc.gov.runtime.runner.bundle.pa.1
  consumes:
  - act.gov.runtime.runner.bundle.pa.1
- id: svc.gov.runtime.runner.bundle.pa.2
  consumes:
  - act.gov.runtime.runner.bundle.pa.2
```
