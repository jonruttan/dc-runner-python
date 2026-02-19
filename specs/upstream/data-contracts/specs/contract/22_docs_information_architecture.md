# Docs Information Architecture v1

## Canonical Surface Split

`docs/` is organized into four canonical surfaces:

- `/docs/book` for user-facing reference manuals.
- `/specs` for executable contracts, schema, conformance, governance, and
  policy sources.
- `/docs/impl` for implementation-specific appendices only.
- `/docs/reviews` for active review prompts/templates/snapshots.
- a separate historical review archive root for archived artifacts only.

`/docs/reviews` is the only valid active review namespace in v1.

## Naming and Index Rules

- Directory index files MUST use `index.md`.
- `README.md` under `/docs/**` is forbidden.
- Filenames MUST be lowercase.
- Word separator is `_`.
- Section separator is `-`.
- Spaces in docs paths are forbidden.
- OS/editor artifact files (for example `.DS_Store`) are forbidden in tracked
  docs paths.

## Enforcement

The layout is machine-enforced by:

- `specs/schema/docs_layout_profile_v1.yaml`
- `scripts/normalize_docs_layout.py`
- governance checks in `./runners/public/runner_adapter.sh --impl rust governance`

This contract is hard-fail in CI (no compatibility window).
