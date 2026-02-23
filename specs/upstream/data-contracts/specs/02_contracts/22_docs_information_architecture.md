# Docs Information Architecture Contract (v1)

Defines canonical docs surfaces for reader navigation and governance coverage.

## Canonical Surfaces

- `docs/book/index.md`
- `docs/book/reference_manifest.yaml`
- `docs/book/reference_index.md`
- `docs/book/reference_coverage.md`
- `docs/book/guides/`

## Audience Paths

- narrative orientation path (`05` -> `15` -> `25`)
- guide-first operational path (`guides/index` -> guide set)
- reference bridge path (`90_reference_guide.md` -> generated references)

## Ownership Boundary

- this repository documents control-plane operation.
- runtime execution details belong in runner repositories.

## Governance

- docs navigation and manifest order MUST stay canonical.
- guide subtree presence and index synchronization MUST be enforced.
