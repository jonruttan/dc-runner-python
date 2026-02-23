```yaml contract-spec
id: DCGOV-SPEC-TOPO-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: specs taxonomy hard-cut layout is canonical
purpose: Ensures governance utility domains are folded under `/specs/governance/*` and prior root shim paths are removed.
type: contract.check
harness:
  root: .
  taxonomy_layout:
    required_paths:
    - /specs/governance/metrics
    - /specs/governance/tools
    - /specs/governance
    - /specs/current.md
    - /specs/01_schema/index.md
    - /specs/02_contracts/index.md
    forbidden_paths:
    - /specs/metrics
    - /specs/tools
    - /specs/pending
    - /specs/schema.md
    - /specs/portable_contract.md
  check:
    profile: governance.scan
    config:
      check: spec.taxonomy_hard_cut_required
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
