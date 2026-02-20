# Governance Cases

## DCGOV-DOCS-REF-010

```yaml contract-spec
id: DCGOV-DOCS-REF-010
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: readme remains implementation-agnostic and canonical for v1 authoring
purpose: Ensures root README stays gateway-oriented, implementation-agnostic, and free from prior assertion-surface
  snippets.
type: contract.check
harness:
  root: .
  readme_coherence:
    path: /README.md
    required_tokens:
    - ./scripts/control_plane.sh critical-gate
    - ./scripts/control_plane.sh governance
    - ./scripts/control_plane.sh docs-generate-check
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
