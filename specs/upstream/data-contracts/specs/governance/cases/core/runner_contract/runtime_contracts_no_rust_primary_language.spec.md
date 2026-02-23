```yaml contract-spec
id: DCGOV-RUNTIME-CONTRACT-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: contracts avoid rust-primary language
purpose: Ensures active contracts remain implementation-agnostic.
type: contract.check
harness:
  root: .
  contract_language:
    files:
    - /specs/02_contracts/10_docs_quality.md
    - /specs/02_contracts/12_runner_interface.md
    - /specs/02_contracts/25_compatibility_matrix.md
    forbidden_tokens:
    - implementation-agnostic
    - required lane
  check:
    profile: governance.scan
    config:
      check: runtime.contracts_no_rust_primary_language
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
