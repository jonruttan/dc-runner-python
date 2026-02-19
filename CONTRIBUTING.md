# Contributing

## Local Setup

Required local tools:

- `bash`
- `python>=3.10`
- `git`

Setup:

```sh
make setup
```

## Required Local Checks

Before opening a PR, run the canonical verification flow:

```sh
make verify
```

## Updating Pinned Upstream Compatibility Snapshot

Canonical specs are owned by `data-contracts`. To bump this runner against a
new upstream version:

```sh
make spec-sync TAG=<upstream-tag-or-ref> SOURCE=<path-or-url>
make verify
```

Review and commit all resulting changes together:

- `/specs/upstream/data_contracts_lock_v1.yaml`
- `/specs/upstream/data-contracts.manifest.sha256`
- `/specs/upstream/data-contracts/**`
- any implementation updates required for compatibility

## Pull Request Expectations

- Keep scope focused and behaviorally coherent.
- Preserve stable runner interface semantics and exit codes.
- Update docs/spec references when behavior or workflows change.
- Update changelog/release notes for user-visible changes.

## Compatibility Invariants Checklist

Do not regress these invariants:

- Stable public command surface in `/runner_adapter.sh`
- Stable exit code semantics (`0/1/2`)
- Deterministic compatibility checks against `/specs/upstream/data-contracts/`

## Reference Docs

- `/docs/architecture.md`
- `/docs/commands.md`
- `/docs/compatibility.md`
- `/docs/release.md`
