# Governance Cases

## DCGOV-DOCS-REF-019

```yaml contract-spec
id: DCGOV-DOCS-REF-019
title: readme includes task-based usage paths
purpose: Ensures README is user-oriented and includes concrete task navigation.
type: contract.check
harness:
  root: .
  readme_usage_paths:
    path: /README.md
    required_tokens:
    - How Users Use This Repository
    - Author a spec change
    - Validate docs and contract coherence
    - Read compatibility and status telemetry
    - Debug governance or docs drift
  check:
    profile: governance.scan
    config:
      check: docs.readme_task_usage_paths_present
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
