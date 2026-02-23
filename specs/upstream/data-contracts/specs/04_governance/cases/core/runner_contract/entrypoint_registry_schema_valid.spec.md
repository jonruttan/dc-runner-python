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
  - id: DCGOV-ENTRY-001
    title: entrypoint registry schema is defined
    purpose: Ensures runner command entrypoint schema is present and canonical.
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
          - type: runtime.runner_command_entrypoints
      - id: assert_2
        assert:
          std.string.contains:
          - var: text
          - pattern: '^dc-runner(\s|$)'
adapters:
- type: beta.check_profile_text_file_config
  actions:
  - id: svc.gov.entry.registry.schema.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.entry.registry.schema.1
  consumes:
  - svc.gov.entry.registry.schema.1
```
