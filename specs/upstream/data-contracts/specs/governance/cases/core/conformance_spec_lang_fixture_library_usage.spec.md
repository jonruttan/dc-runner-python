```yaml contract-spec
id: DCGOV-CONF-LIB-EXPR-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: spec_lang conformance fixture uses shared helper library calls
purpose: Ensures spec_lang conformance fixtures reuse shared conformance helper library functions
  for repeated expression patterns.
type: contract.check
harness:
  root: .
  spec_lang_fixture_library_usage:
    path: /specs/conformance/cases/core/spec_lang.spec.md
    required_library_path: /specs/libraries/conformance/assertion_core.spec.md
    required_call_prefix: conf.
    min_call_count: 4
    required_case_ids:
    - DCCONF-EXPR-001
    - DCCONF-EXPR-002
    - DCCONF-EXPR-008
  check:
    profile: governance.scan
    config:
      check: conformance.spec_lang_fixture_library_usage
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
      - conformance.spec_lang_fixture_library_usage
    imports:
    - from: artifact
      names:
      - summary_json
```
