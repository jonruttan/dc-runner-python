# Governance Cases

## DCGOV-ASSERT-PROFILE-004

```yaml contract-spec
id: DCGOV-ASSERT-PROFILE-004
title: domain conformance checks are library-backed
purpose: Ensures domain conformance checks use harness.spec_lang domain libraries rather than
  ad hoc inline-only policy.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: assert.domain_library_usage_required
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
