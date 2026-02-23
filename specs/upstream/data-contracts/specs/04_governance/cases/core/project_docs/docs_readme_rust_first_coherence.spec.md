```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
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
      - /specs/01_schema/schema_v1.md
      - /specs/02_contracts/index.md
      - /specs/02_contracts/25_compatibility_matrix.md
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
    - ref: /specs/05_libraries/policy/policy_assertions.spec.md
      as: lib_policy_core_spec
      symbols:
      - policy.assert.no_violations
      - policy.assert.summary_passed
      - policy.assert.summary_check_id
      - policy.assert.scan_pass
contracts:
  clauses:
  - id: DCGOV-DOCS-REF-010
    title: readme remains implementation-agnostic and canonical for v1 authoring
    purpose: Ensures root README stays gateway-oriented, implementation-agnostic,
      and free from canonical assertion-surface snippets.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.readme.rust.first.c.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.readme.rust.first.c.1
  consumes:
  - act.gov.docs.readme.rust.first.c.1
```
