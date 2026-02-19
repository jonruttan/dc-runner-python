# Governance Cases

## DCGOV-SPEC-TOPO-001

```yaml contract-spec
id: DCGOV-SPEC-TOPO-001
title: specs taxonomy hard-cut layout is canonical
purpose: Ensures governance utility domains are folded under `/specs/governance/*` and legacy root shim paths are removed.
type: contract.check
harness:
  root: .
  taxonomy_layout:
    required_paths:
    - /specs/governance/metrics
    - /specs/governance/tools
    - /specs/governance/pending
    - /specs/current.md
    - /specs/schema/index.md
    - /specs/contract/index.md
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
