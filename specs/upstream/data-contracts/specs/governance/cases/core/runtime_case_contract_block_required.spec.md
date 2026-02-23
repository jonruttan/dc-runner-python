```yaml contract-spec
id: DCGOV-RUNTIME-CONTRACT-BLOCK-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: cases must use contract block
purpose: Enforces top-level contract block requirement for executable cases.
type: contract.check
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
harness:
  check:
    profile: governance.scan
    config:
      check: runtime.case_contract_block_required
```
