# Governance Cases

## DCGOV-DOCS-REF-010

```yaml contract-spec
id: DCGOV-DOCS-REF-010
title: readme remains rust-first and canonical for v1 authoring
purpose: Ensures root README stays gateway-oriented, rust-first, and free from legacy assertion-surface
  snippets.
type: contract.check
harness:
  root: .
  readme_coherence:
    path: /README.md
    required_tokens:
    - ./runners/public/runner_adapter.sh --impl rust critical-gate
    - ./runners/public/runner_adapter.sh --impl rust governance
    - ./runners/public/runner_adapter.sh --impl rust docs-generate-check
    - Compatibility Matrix (Non-Blocking)
    - compatibility_non_blocking
    - SPEC_PREPUSH_BYPASS=1 git push
    required_paths:
    - /docs/book/index.md
    - /docs/book/99_generated_reference_index.md
    - /specs/schema/schema_v1.md
    - /specs/contract/index.md
    - /specs/contract/25_compatibility_matrix.md
    forbidden_tokens:
    - 'target:'
    - '''on'':'
    - 'asserts:'
    - evaluate wrapper
  check:
    profile: governance.scan
    config:
      check: docs.readme_rust_first_coherence
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
