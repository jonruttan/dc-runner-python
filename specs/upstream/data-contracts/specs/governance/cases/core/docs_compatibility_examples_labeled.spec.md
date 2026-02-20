# Governance Cases

## DCGOV-DOCS-REF-008

```yaml contract-spec
id: DCGOV-DOCS-REF-008
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: compatibility examples are explicitly labeled
purpose: Ensures active documentation keeps Rust as canonical and labels Python/PHP examples
  as non-blocking compatibility lanes.
type: contract.check
harness:
  root: .
  compatibility_docs:
    files:
    - /README.md
    - /docs/development.md
    - /specs/contract/12_runner_interface.md
    
    required_tokens:
    - implementation-agnostic
    - compatibility lanes
    - non-blocking
    forbidden_tokens:
    - ./scripts/core_gate.sh
  check:
    profile: governance.scan
    config:
      check: docs.compatibility_examples_labeled
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
