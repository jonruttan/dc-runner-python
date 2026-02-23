# Contract Bundle Taxonomy Contract (v1)

Defines canonical bundle terminology for project-scoped validation and artifact generation.

## Canonical Hierarchy

Canonical hierarchy is:

- `Bundle -> Domain -> Module -> Contract`

Hierarchy rules:

- `Bundle` is the top-level canonical unit.
- `Domain` is a functional partition within a bundle (for example `tooling`, `docs`, `source`).
- `Module` is a cohesive capability inside a domain.
- `Contract` is the executable spec unit.

## Bundle Terms

- `Asset`: consumed static resource declared by `contract-spec` (`assets[]`).
- `Artifact`: produced output resource declared by `contract-spec` (`artifacts[]`).
- `Bundle Package`: downloadable immutable materialization of a bundle version.
- `Bundle Manifest`: machine-readable descriptor of bundle structure and metadata.
- `Bundle Lock`: resolved immutable record that captures selected content and integrity hashes.

Trigger semantics are out of scope for this taxonomy version.

## Canonical Metadata Vocabulary

Bundle metadata uses:

- `bundle_id` (string)
- `bundle_version` (SemVer string)
- `maintainers[]` (owner list)

`bundle_version` and `maintainers` are canonical names for new bundle metadata.

## Canonical Vocabulary

Use canonical bundle terminology in all active surfaces:

- `bundle_id` for bundle identity.
- `bundle_version` for bundle version metadata.
- `maintainers` for ownership metadata.
- avoid ambiguous bare `version` in bundle metadata contexts.
- treat `assets[]` / `artifacts[]` semantics as canonical contract authority in
  `data-contracts`; bundle manifests are derived package metadata.
