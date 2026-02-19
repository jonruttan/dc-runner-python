# Governance Cases

## DCGOV-STDLIB-004

```yaml contract-spec
id: DCGOV-STDLIB-004
title: stdlib conformance coverage files are present
purpose: Ensures canonical stdlib conformance fixtures are present and discoverable.
type: contract.check
harness:
  root: .
  stdlib_conformance:
    required_paths:
    - /specs/conformance/cases/core/spec_lang_stdlib.spec.md
    - /specs/conformance/cases/core/spec_lang_schema.spec.md
  check:
    profile: governance.scan
    config:
      check: spec_lang.stdlib_conformance_coverage
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
```
