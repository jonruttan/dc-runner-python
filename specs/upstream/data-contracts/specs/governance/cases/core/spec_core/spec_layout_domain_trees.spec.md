```yaml contract-spec
id: DCGOV-SPECLAYOUT-DOMAIN-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec layout uses domain tree directories
purpose: Ensures conformance, governance, and library specs are organized under domain subdirectories
  with index files.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: spec.layout_domain_trees
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
    - summary_json
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - spec.layout_domain_trees
```
