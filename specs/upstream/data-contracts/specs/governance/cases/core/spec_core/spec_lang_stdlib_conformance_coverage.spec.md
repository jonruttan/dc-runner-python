```yaml contract-spec
id: DCGOV-STDLIB-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: stdlib conformance coverage files are present
purpose: Ensures canonical stdlib conformance fixtures are present and discoverable.
type: contract.check
harness:
  root: .
  stdlib_conformance:
    required_paths:
    - /specs/03_conformance/cases/core/spec_lang_stdlib.spec.md
    - /specs/03_conformance/cases/core/spec_lang_schema.spec.md
  check:
    profile: governance.scan
    config:
      check: spec_lang.stdlib_conformance_coverage
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
```
