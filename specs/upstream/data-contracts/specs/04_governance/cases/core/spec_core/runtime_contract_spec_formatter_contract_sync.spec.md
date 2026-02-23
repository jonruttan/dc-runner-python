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
        path: /specs/01_schema/runner_cli_contract_v1.yaml
contracts:
  clauses:
  - id: DCGOV-RUNTIME-RCLI-006
    title: contract spec formatter command contract is synchronized
    purpose: Ensures runner CLI contract docs and schema include the contract-spec-format
      command surface and mode metadata.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - std.string.contains:
          - var: text
          - contract-spec-format
        - std.string.contains:
          - var: text
          - --check
        - std.string.contains:
          - var: text
          - --write
adapters:
- type: beta.check_profile_text_file_config_path_specs_contract_29_runner_cli_interface_md
  actions:
  - id: act.gov.runtime.contract.spec.fo.1
    profile: default
- type: beta.check_profile_text_file_config_path_specs_schema_runner_cli_contract_v1_yaml
  actions:
  - id: act.gov.runtime.contract.spec.fo.2
    profile: default
services:
- id: svc.gov.runtime.contract.spec.fo.1
  consumes:
  - act.gov.runtime.contract.spec.fo.1
- id: svc.gov.runtime.contract.spec.fo.2
  consumes:
  - act.gov.runtime.contract.spec.fo.2
```
