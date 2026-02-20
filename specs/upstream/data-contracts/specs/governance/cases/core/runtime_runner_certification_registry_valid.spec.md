# Governance Cases

## DCGOV-RUNTIME-CERT-001

```yaml contract-spec
id: DCGOV-RUNTIME-CERT-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: runner certification registry shape is valid
purpose: Ensures runner certification registry entries are complete and deterministic.
type: contract.check
harness:
  root: .
  runner_certification:
    path: /specs/schema/runner_certification_registry_v1.yaml
    required_runner_ids:
    - rust
    - python
    - php
    - node
    - c
  check:
    profile: governance.scan
    config:
      check: runtime.runner_certification_registry_valid
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
