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
        path: /README.md
contracts:
  clauses:
  - id: DCGOV-RUNTIME-BUNDLE-004
    title: canonical bundle librarian repository is documented
    purpose: Ensures canonical bundle source points to data-contracts-bundles and
      not local specs/bundles manifests.
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
          std.logic.not:
            std.string.contains:
            - var: text
            - /specs/bundles/index.md
adapters:
- type: beta.check_profile_text_file_config_path_readme_md
  actions:
  - id: act.gov.runtime.bundle.librarian.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.bundle.librarian.1
  consumes:
  - act.gov.runtime.bundle.librarian.1
```
