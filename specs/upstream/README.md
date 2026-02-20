# Upstream Snapshots

This directory stores pinned snapshots consumed by `dc-runner-python`.

## Global Contracts (`data-contracts`)

- Snapshot: `/specs/upstream/data-contracts/`
- Lock: `/specs/upstream/data_contracts_lock_v1.yaml`
- Manifest: `/specs/upstream/data-contracts.manifest.sha256`

Update:

```sh
make spec-sync TAG=<tag-or-ref> SOURCE=<path-or-url>
```

Check:

```sh
make spec-sync-check
```

## Runner-Specific Contracts (`dc-runner-spec`)

- Snapshot: `/specs/upstream/dc-runner-spec/`
- Lock: `/specs/upstream/dc_runner_spec_lock_v1.yaml`
- Manifest: `/specs/upstream/dc-runner-spec.manifest.sha256`

Update:

```sh
make runner-spec-sync TAG=<tag-or-ref> SOURCE=<path-or-url>
```

Check:

```sh
make runner-spec-check
```
