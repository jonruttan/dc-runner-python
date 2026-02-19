# dc-runner-python

Python compatibility runner for Data Contracts.

## Scope

- Owns Python compatibility execution surfaces formerly hosted in monorepo path `runners/python`.
- Non-blocking lane relative to required Rust lane.

## Commands

- `python -m spec_runner.spec_lang_commands run-governance-specs --liveness-level basic`
- `python -m spec_runner.spec_lang_commands compare-conformance-parity --python-only --cases specs/conformance/cases --out .artifacts/conformance-parity-python.json`

## Local setup

```sh
python -m pip install -e '.[dev]'
```

## Implementation Specs

Runner-owned implementation contracts live in:

- `specs/impl/python/`

## Source Moved From data-contracts

Implementation narratives previously documented in `data-contracts/docs/impl/python.md`
are owned here. See `docs/migration_from_data_contracts.md` for migration
mapping.
