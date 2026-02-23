# Repository Boundary Charter

Source of truth: spec.repo_boundary_charter

This charter defines ownership boundaries between canonical schema contracts and reusable runner-oriented spec contracts.

## Ownership

- `data-contracts` owns canonical schema, contract, conformance, governance, and policy semantics.
- `data-contracts-library` owns reusable runner-oriented behavior specs, runner overlays, and shared reusable libraries.

## Canonical Authority

- Canonical schema authority is `data-contracts` `/specs/01_schema/schema_v1.md`.
- Reusable runner-owned executable cases in `data-contracts-library` consume schema authority via `schema_ref: /specs/01_schema/schema_v1.md`.

## Forbidden Crossings in Canonical Trees

Canonical `data-contracts` trees must not contain internal reusable-runner tree surface tokens.

Reusable runner implementation references must use explicit external repository paths, for example:

- `/data-contracts-library/specs/07_runner_behavior/impl/...`
- `/data-contracts-library/specs/07_runner_behavior/contract_sets/...`

## Enforcement

- Governance hard-fails when forbidden boundary tokens appear in canonical trees.
- Runner-specific behavior validation remains reusable-runner-owned and is not redefined inside canonical schema docs.
- Canonical shared libraries and overlay manifests must reference `data-contracts-library`; new `*-spec` repositories are noncanonical.
