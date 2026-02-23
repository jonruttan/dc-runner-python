```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    check:
      profile: text.file
      config: {}
contracts:
  clauses:
  - id: DCGOV-ENTRY-003
    title: entrypoint artifact contract is complete
    purpose: Ensures required command artifacts are declared in the entrypoint contract.
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
          - /.artifacts/governance-summary.json
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - /.artifacts/critical-gate-summary.json
adapters:
- type: beta.check_profile_text_file_config
  actions:
  - id: svc.gov.entry.artifact.contract.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.entry.artifact.contract.1
  consumes:
  - svc.gov.entry.artifact.contract.1
```
