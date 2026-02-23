# Upstream Snapshots

This directory stores pinned snapshots consumed by this runner repository.

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

## Runner Contracts (`data-contracts-library`)

- Snapshot: `/specs/upstream/data-contracts-library/`
- Lock: `/specs/upstream/resolved_contract_set_lock_v1.yaml`
- Lock Hash: `/specs/upstream/resolved_contract_set_lock_v1.sha256`
- Manifest: `/specs/upstream/data-contracts-library.manifest.sha256`

Update:

```sh
make runner-spec-sync TAG=<tag-or-ref> SOURCE=<path-or-url>
```

Check:

```sh
make runner-spec-check
```
