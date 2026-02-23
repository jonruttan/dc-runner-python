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
        path: /specs/02_contracts/34_runner_implementation_spec_bundles.md
contracts:
  clauses:
  - id: DCGOV-RUNTIME-BUNDLE-005
    title: implementation overlay bundle contract is defined
    purpose: Ensures implementation overlay bundle contract documents canonical base
      source, checksum requirements, and patch-based semantics.
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
          - data-contracts-bundles
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - checksum
      - id: assert_3
        assert:
          std.string.contains:
          - var: text
          - add_files
      - id: assert_4
        assert:
          std.string.contains:
          - var: text
          - replace_files
      - id: assert_5
        assert:
          std.string.contains:
          - var: text
          - delete_paths
      - id: assert_6
        assert:
          std.string.contains:
          - var: text
          - Full copied canonical trees are not the normative model.
adapters:
- type: beta.check_profile_text_file_config_path_specs_contract_34_runner_implementation_spec_bundles_md
  actions:
  - id: act.gov.runtime.impl.bundle.over.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.impl.bundle.over.1
  consumes:
  - act.gov.runtime.impl.bundle.over.1
```
