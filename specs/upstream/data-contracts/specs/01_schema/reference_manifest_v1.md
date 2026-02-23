# Reference Manifest Schema (v1)

The reference manifest is the canonical machine-readable source for generated
reference index and coverage artifacts.

Path:

- `docs/book/reference_manifest.yaml`

Shape:

```yaml
version: 1
title: Data Contracts Reference Manual
chapters:
- path: /docs/book/10_getting_started.md
  summary: first-run setup and safety model.
  contract_refs:
  - specs/02_contracts/10_docs_quality.md
```

Required fields:

- `version` (int): must be `1`
- `chapters` (list[mapping], non-empty)

`chapters[*]` required fields:

- `path` (string): chapter markdown path
- `summary` (string): one-line chapter purpose

Optional fields:

- `title` (string)
- `contract_refs` (list[string]): related normative contracts

Generation/verification:

- `scripts/docs_build_reference.py` renders:
  - `docs/book/reference_index.md`
  - `docs/book/reference_coverage.md`
  - `docs/book/docs_graph.json`
- `scripts/docs_build_reference.py --check` fails when generated files are out
  of date with manifest + docs metadata.
