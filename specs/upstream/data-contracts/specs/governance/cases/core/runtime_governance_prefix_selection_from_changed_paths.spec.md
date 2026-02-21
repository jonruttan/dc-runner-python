```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-011
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: governance triage selects prefixes from changed paths
type: contract.check
purpose: Ensures triage auto mode derives targeted check prefixes from changed paths before
  fallback prefixes.
harness:
  root: .
  triage_prefix_selection:
    path: /scripts/governance_triage.sh
    required_tokens:
    - collect_changed_paths
    - select_prefixes_from_changed_paths
    - selection_source="changed_paths"
    - CHECK_PREFIXES
  check:
    profile: governance.scan
    config:
      check: runtime.governance_prefix_selection_from_changed_paths
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
