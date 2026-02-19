# Governance Cases

## DCGOV-RUNTIME-CONTRACT-001

```yaml contract-spec
id: DCGOV-RUNTIME-CONTRACT-001
title: contracts avoid rust-primary language
purpose: Ensures active contracts remain implementation-agnostic.
type: contract.check
harness:
  root: .
  contract_language:
    files:
    - /specs/contract/10_docs_quality.md
    - /specs/contract/12_runner_interface.md
    - /specs/contract/25_compatibility_matrix.md
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
