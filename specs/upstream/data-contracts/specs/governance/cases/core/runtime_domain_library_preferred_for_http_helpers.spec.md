```yaml contract-spec
id: DCGOV-DOMAIN-LIB-HTTP-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http context assertions prefer domain http helpers
purpose: Enforces `domain.http.*` helper usage for oauth meta assertions in api.http cases
  instead of raw std.object.get projection chains.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.domain_library_preferred_for_http_helpers
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
        - passed
      - true
```
