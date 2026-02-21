```yaml contract-spec
id: DCGOV-DOCS-CANON-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: governance check family map covers all registered checks
purpose: Ensures each governance check id is mapped to a canonical check family prefix.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.governance_check_family_map_complete
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
