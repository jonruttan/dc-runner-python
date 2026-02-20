# Migration From data-contracts

This runner repo now owns Python implementation details formerly documented in `data-contracts`.

Former locations in `data-contracts`:
- `docs/impl/python.md`
- `specs/impl/**` implementation narratives

Canonical runner-specific spec ownership now lives in:
- `dc-runner-spec/specs/impl/python/`

This repository consumes that canonical source via:
- `/specs/upstream/dc-runner-spec/specs/impl/python/`
- `/specs/impl/python/index.md` (local pointer)
