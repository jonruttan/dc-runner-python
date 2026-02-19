# Governance Cases

## DCGOV-DOCS-CANON-003

```yaml contract-spec
id: DCGOV-DOCS-CANON-003
title: docs freshness strict checker passes
purpose: Ensures specs freshness checks are strict, deterministic, and currently clean.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.canonical_freshness_strict
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
