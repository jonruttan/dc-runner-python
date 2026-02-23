```yaml contract-spec
id: DCGOV-DOCS-QUAL-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: reference index is generated from manifest
purpose: Ensures reference index markdown remains synchronized with the manifest source of
  truth.
type: contract.check
harness:
  root: .
  docs_quality:
    manifest: docs/book/reference_manifest.yaml
    index_out: /docs/book/reference_index.md
  check:
    profile: governance.scan
    config:
      check: docs.reference_manifest_sync
  use:
  - ref: /specs/05_libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.reference_manifest_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
