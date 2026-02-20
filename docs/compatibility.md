# Compatibility

`dc-runner-python` consumes two pinned upstream snapshots:

1. Global contracts from `data-contracts`.
2. Python runner-specific contracts from `dc-runner-spec`.

Artifacts:

- `/specs/upstream/data_contracts_lock_v1.yaml`
- `/specs/upstream/data-contracts.manifest.sha256`
- `/specs/upstream/dc_runner_spec_lock_v1.yaml`
- `/specs/upstream/dc-runner-spec.manifest.sha256`

Verification gates:

```sh
make spec-sync-check
make compat-check
make runner-spec-check
```

`make verify` is blocking and includes all of the above.
