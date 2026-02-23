```yaml contract-spec
id: DCGOV-PACK-006
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: pack case ids remain unique
purpose: Ensures newly introduced runner-cli cases do not collide on case id.
type: contract.check
harness:
  root: .
  runner_cli_cases:
    path: /specs/03_conformance/cases/runner_cli
    required_ids:
      - DCCONF-RCLI-001
      - DCCONF-RCLI-002
      - DCCONF-RCLI-003
      - DCCONF-RCLI-004
      - DCCONF-RCLI-005
  check:
    profile: governance.scan
    config:
      check: packs.pack_case_ids_unique
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names: [violation_count]
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
```
