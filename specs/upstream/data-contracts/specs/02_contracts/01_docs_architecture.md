# Docs Architecture Contract

Source of truth: spec.contract.docs_architecture

## Canonical Ownership

- `/specs/00_core/current.md` is the active model snapshot entrypoint.
- `/specs/01_schema/**` owns case-shape, schema registry, and profile contracts.
- `/specs/02_contracts/**` owns normative policy/traceability contracts.
- `/specs/04_governance/**` owns executable governance checks.
- `/specs/05_libraries/**` owns reusable spec-lang library surfaces.
- `external runner spec repository specs/**` owns implementation fixture suites.

## Generated References

Generated appendices in `/docs/book/9*.md` are derived artifacts and must be regenerated from canonical sources.

## Historical Content

- `/docs/history/**` is archival and informational.
