# Governance Cases

## DCGOV-RUNTIME-TRIAGE-005

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-005
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: triage parser derives failing check ids and prefixes
purpose: Ensures triage script parses governance ERROR lines and maps check ids to check-prefix
  retries.
type: contract.check
harness:
  root: .
  triage_failure_parser:
    path: /scripts/governance_triage.sh
    required_tokens:
    - '^ERROR: ([A-Z0-9-]+):'
    - parse_error_ids_from_output
    - build_prefixes_from_ids
    - specs/governance/check_prefix_map_v1.yaml
  check:
    profile: governance.scan
    config:
      check: runtime.triage_failure_id_parsing_required
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
