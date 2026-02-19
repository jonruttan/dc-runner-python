# Upstream Snapshot

This directory stores a pinned compatibility snapshot of Data Contracts specs
consumed by `dc-runner-python`.

Source of truth:

- `/specs/upstream/data_contracts_lock_v1.yaml` (upstream repo/tag-or-ref/commit + integrity)
- `/specs/upstream/data-contracts.manifest.sha256` (deterministic file manifest)
- `/specs/upstream/data-contracts/` (vendored spec snapshot used for compatibility verification)

Update flow:

```sh
make spec-sync TAG=<upstream-tag-or-ref> SOURCE=<path-or-url>
make verify
```

Integrity check:

```sh
make spec-sync-check
```

Related docs:

- `/docs/compatibility.md`
- `/docs/release.md`

Canonical global command-contract jobs are sourced from:

- `/specs/upstream/data-contracts/specs/conformance/cases/core/report_job_contracts.spec.md`
- `/specs/upstream/data-contracts/specs/conformance/cases/core/script_job_contracts.spec.md`
