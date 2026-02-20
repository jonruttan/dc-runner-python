# Governance Cases

## DCGOV-DOCS-QUAL-004

```yaml contract-spec
id: DCGOV-DOCS-QUAL-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: doc token dependencies resolve to owner docs
purpose: Ensures required tokens in doc metadata are owned and present in owner docs.
type: contract.check
harness:
  root: .
  docs_quality:
    manifest: docs/book/reference_manifest.yaml
  check:
    profile: governance.scan
    config:
      check: docs.token_dependency_resolved
  use:
  - ref: /specs/libraries/policy/policy_core.spec.md
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
      - docs.token_dependency_resolved
    imports:
    - from: artifact
      names:
      - summary_json
```
