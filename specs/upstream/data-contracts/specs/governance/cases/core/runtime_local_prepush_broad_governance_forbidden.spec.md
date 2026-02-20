# Governance Cases

## DCGOV-RUNTIME-TRIAGE-009

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-009
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: local prepush does not require broad governance
type: contract.check
purpose: Ensures local parity flow keeps broad governance out of default prepush path.
harness:
  root: .
  local_prepush_broad_forbidden:
    path: /scripts/local_ci_parity.sh
    required_tokens:
    - skip broad governance (set SPEC_PREPUSH_REQUIRE_BROAD=1 to enable)
    - SPEC_PREPUSH_REQUIRE_BROAD=1
    forbidden_tokens:
    - run_step governance "${SPEC_RUNNER_BIN}" governance
  check:
    profile: governance.scan
    config:
      check: runtime.local_prepush_broad_governance_forbidden
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
