# Governance Cases

## DCGOV-DOCS-NAME-001

```yaml contract-spec
id: DCGOV-DOCS-NAME-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: docs filenames follow lowercase separator policy
purpose: Enforces deterministic docs filename shape using underscores for words and hyphens
  for section separators.
type: contract.check
harness:
  root: .
  filename_policy:
    paths:
    - docs
    include_extensions:
    - .md
    - .yaml
    - .yml
    - .json
    allow_exact:
    - README.md
    allowed_name_regex: ^[a-z0-9]+(?:_[a-z0-9]+)*(?:-[a-z0-9]+(?:_[a-z0-9]+)*)*(?:\.spec)?\.(?:md|yaml|yml|json)$
  check:
    profile: governance.scan
    config:
      check: naming.filename_policy
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
      - naming.filename_policy
    imports:
    - from: artifact
      names:
      - summary_json
```
