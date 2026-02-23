# Docs Information Architecture Contract (v1)

Defines canonical docs surfaces for reader navigation and governance coverage.

## Canonical Surfaces

- `docs/book/index.md`
- `docs/book/reference_manifest.yaml`
- `docs/book/reference_index.md`
- `docs/book/reference_coverage.md`
- `docs/book/guides/`

## Audience Paths

- orientation/tutorial path (`05` -> `30`)
- guide-first operational path (`35` -> `guides/index` -> guide set)
- reference bridge path (`90_reference_guide.md` -> `99_generated_reference_index.md`)

## Ownership Boundary

- this repository documents control-plane operation.
- runtime execution details belong in runner repositories.

## Governance

- docs navigation and manifest order MUST stay canonical.
- guide subtree presence and index synchronization MUST be enforced.
