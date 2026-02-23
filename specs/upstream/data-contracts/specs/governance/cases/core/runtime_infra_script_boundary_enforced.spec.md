```yaml contract-spec
id: DCGOV-RUNTIME-SHELL-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: infra script boundary enforced
purpose: Ensures ingest script remains transport/integration oriented and does not import governance policy docs.
type: contract.check
harness:
  root: .
  ingest_script:
    path: /scripts/runner_status_ingest.sh
    required_tokens:
      - require_tool curl
      - require_tool jq
      - require_tool shasum
    forbidden_tokens:
      - specs/contract/policy_v1.yaml
      - check_sets_v1.yaml
  check:
    profile: governance.scan
    config:
      check: runtime.infra_script_boundary_enforced
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
