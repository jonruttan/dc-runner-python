# dc-runner-python

Python implementation lane for Data Contracts runner compatibility.

## What This Project Is

`dc-runner-python` provides Python runner interfaces and compatibility checks for
Data Contracts workflows. It verifies behavior against a pinned upstream specs
snapshot so compatibility changes are explicit and reviewable.

## What Is Data Contracts?

[Data Contracts](https://github.com/jonruttan/data-contracts) is the canonical
contracts/specifications project for the runner ecosystem. It owns normative
contracts, schemas, conformance surfaces, and governance policy.

This repository does not redefine those canonical contracts. It owns Python
implementation behavior and compatibility verification against pinned upstream
versions.

## Responsibility Boundary

- `data-contracts` owns canonical runner specs/contracts and evolution.
- `dc-runner-python` owns Python implementation behavior and compatibility checks.

## Stable Interface Contract

- Public runner entrypoint: `/runner_adapter.sh`
- Stable exit code semantics:
  - `0` success
  - `1` runtime/tool failure
  - `2` invalid usage/config

## Quickstart

Setup:

```sh
make setup
```

Core checks:

```sh
make lint
make typecheck
make smoke
```

Full local verification:

```sh
make verify
```

## Upstream Snapshot Workflow

Pinned upstream compatibility artifacts:

- `/specs/upstream/data_contracts_lock_v1.yaml`
- `/specs/upstream/data-contracts.manifest.sha256`
- `/specs/upstream/data-contracts/`

Update pinned snapshot:

```sh
make spec-sync TAG=<upstream-tag-or-ref> SOURCE=<path-or-url>
```

Validate lock/snapshot integrity:

```sh
make spec-sync-check
```

Run compatibility verification:

```sh
make compat-check
```

## Documentation Map

- Architecture: `/docs/architecture.md`
- Commands: `/docs/commands.md`
- Compatibility: `/docs/compatibility.md`
- Release operations: `/docs/release.md`
- Contributor workflow: `/CONTRIBUTING.md`

## Specs Map

- Local runner-owned implementation specs:
  - `/specs/impl/python/`
- Upstream pinned compatibility snapshot:
  - `/specs/upstream/data-contracts/`

## Source Moved From data-contracts

Implementation narratives previously in `data-contracts/docs/impl/python.md` are
owned here. See `/docs/migration_from_data_contracts.md`.
