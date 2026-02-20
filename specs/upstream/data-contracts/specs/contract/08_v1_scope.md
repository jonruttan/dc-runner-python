# V1 Scope And Compatibility Commitments

This document defines explicit v1 boundaries for `data-contracts` so adoption and
maintenance decisions stay predictable.

## V1 In Scope

- Execute Markdown-embedded `yaml contract-spec` blocks for core types:
  - `text.file`
  - `cli.run`
- Require explicit schema pinning for every executable case:
  - `spec_version: 1`
  - `schema_ref: /specs/schema/schema_v1.md`
- Enforce stable case shape and assertion DSL from:
  - `specs/schema/schema_v1.md`
  - `specs/schema/schema_catalog_v1.yaml`
  - `specs/contract/`
  - `specs/schema/registry/v1/*.yaml` (machine source of truth)
- Maintain deterministic conformance and parity checks across:
  - Python runner
  - PHP runner
- Runtime scope is explicitly bounded in v1:
  - only Python and PHP are required support targets
  - additional runtimes require explicit contract/governance expansion
  - required support targets in v1 are exactly: Python runner, PHP runner
- Keep a dependency-minimal core suitable for library reuse.

## V1 Non-Goals

- No sandboxing of untrusted specs or runner isolation guarantees.
- No expansion into a broad generalized workflow engine.
- No requirement to support all implementation-specific harness features in the
  portable contract.
- No guarantee that project-specific adapters/harnesses are portable across
  runtimes.

## Compatibility Commitments (v1)

- Existing v1 canonical DSL forms (`must` / `can` / `cannot`, `contain`,
  `regex`) remain stable.
- Current-spec-only rule (pre-v1):
  - docs and runtime behavior MUST describe and execute only the current schema
  - do not add wording about prior schema forms
  - do not add compatibility code paths that rewrite/accept prior schema forms
- Governance checks SHOULD keep rule-data (for example token/regex lists) in
  governance `.spec.md` harness config instead of hardcoded script globals.
- Contract-breaking changes require versioning:
  - update policy lifecycle metadata (`introduced_in` / `removed_in`)
  - update schema/contract docs and traceability in the same change slice
  - include conformance or unit evidence for changed `MUST` behavior
- Portable conformance case format remains Markdown `*.spec.md` with fenced
  `yaml contract-spec` blocks.
- Canonical executable surfaces are markdown-only:
  - conformance cases (`specs/conformance/cases`)
  - governance cases (`specs/governance/cases`)
  - impl executable cases (`runner-owned implementation specs`)
  - spec-lang library cases (`specs/libraries`)
- Machine data artifacts remain YAML/JSON (baselines/manifests/generated
  reports/schema profiles) and are non-executable surfaces.

## Release Boundary

`data-contracts` v1 readiness requires:

- deterministic CI gate (`./scripts/ci_gate.sh`) green
- contract governance checks green
- conformance parity check green for the canonical case set
- no unresolved P0/P1 contract risks in active review backlog
