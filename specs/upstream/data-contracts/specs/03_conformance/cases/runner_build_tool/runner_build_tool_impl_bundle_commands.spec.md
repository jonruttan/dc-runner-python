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
  - id: DCCONF-BTOOL-010
    title: implementation bundle contract defines build and package command surface
    purpose: Runner implementation spec bundle contract must expose build-impl, package-impl,
      and package-check command vocabulary.
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
          - build-impl
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - package-impl
      - id: assert_3
        assert:
          std.string.contains:
          - var: text
          - package-check
      - id: assert_4
        assert:
          std.string.contains:
          - var: text
          - data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz
adapters:
- type: beta.check_profile_text_file_config_path_specs_contract_34_runner_implementation_spec_bundles_md
  actions:
  - id: act.conf.runner.build.tool.impl.b.1
    direction: bidirectional
    profile: default
services:
- id: svc.conf.runner.build.tool.impl.b.1
  consumes:
  - act.conf.runner.build.tool.impl.b.1
```
