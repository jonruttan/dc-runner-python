# Docs Architecture Contract

Source of truth: spec.contract.docs_architecture

## Canonical Ownership

- `/specs/current.md` is the active model snapshot entrypoint.
- `/specs/schema/**` owns case-shape, schema registry, and profile contracts.
- `/specs/contract/**` owns normative policy/traceability contracts.
- `/specs/governance/**` owns executable governance checks.
- `/specs/libraries/**` owns reusable spec-lang library surfaces.
- `runner-owned implementation specs/**` owns implementation fixture suites.

## Generated References

Generated appendices in `/docs/book/9*.md` are derived artifacts and must be regenerated from canonical sources.

## Non-canonical Historical Content

- `/docs/history/**` is archival and non-canonical.
