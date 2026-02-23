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
        path: /specs/01_schema/schema_v1.md
contracts:
  clauses:
  - id: DCGOV-NORM-007
    title: v1 contract spec key order contract is documented
    purpose: Ensures schema v1 documents canonical suite-root and contract-item key
      ordering for formatter enforcement.
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
          - '## v1 Canonical Key Order (Formatter Scope)'
        - std.string.contains:
          - var: text
          - Suite root canonical order
        - std.string.contains:
          - var: text
          - contracts[] canonical order
        - std.string.contains:
          - var: text
          - '`spec_version`'
        - std.string.contains:
          - var: text
          - '`contracts`'
        - std.string.contains:
          - var: text
          - list item order is preserved as-authored
adapters:
- type: beta.check_profile_text_file_config_path_specs_schema_schema_v1_md
  actions:
  - id: act.gov.normalization.contract.s.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.normalization.contract.s.1
  consumes:
  - act.gov.normalization.contract.s.1
```
