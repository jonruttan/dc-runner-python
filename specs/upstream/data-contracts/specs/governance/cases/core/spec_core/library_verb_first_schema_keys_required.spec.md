```yaml contract-spec
id: DCGOV-LIB-VERB-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: library schema uses verb-first key names
purpose: Ensures spec_lang.export authoring uses defines.public/defines.private and rejects
  non-canonical definitions keys.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: library.verb_first_schema_keys_required
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
      - library.verb_first_schema_keys_required
```
