# Commands

## Maintainer Command Reference

### Setup

```sh
make setup
```

### Lint and typecheck

```sh
make lint
make typecheck
```

### Smoke

```sh
make smoke
```

### Full verification

```sh
make verify
```

### Upstream compatibility snapshot update

```sh
make spec-sync TAG=<upstream-tag-or-ref> SOURCE=<path-or-url>
```

### Upstream snapshot integrity check

```sh
make spec-sync-check
```

Optional explicit source resolution check:

```sh
make spec-sync-check SOURCE=https://github.com/jonruttan/data-contracts.git
```

### Runner compatibility check

```sh
make compat-check
```

## Exit Behavior

Runner command contract (via `/runner_adapter.sh`):

- `0`: success
- `1`: runtime/tool failure
- `2`: usage/config error

Script/check failures return non-zero and should be treated as merge-blocking.

## Troubleshooting

| Symptom | Likely Cause | Action |
|---|---|---|
| `spec-sync-check` fails manifest drift | Snapshot changed without lock/manifest update | Re-run `make spec-sync TAG=...` and commit lock+manifest+snapshot |
| `compat-check` fails required subcommand check | Adapter command surface drift | Compare `/runner_adapter.sh` with required local compatibility commands |
| `compat-check` fails lock tag resolution with `SOURCE=` | Upstream ref/tag changed or unavailable | Verify upstream ref exists or use local source path |
| `make verify` fails lint/typecheck | Python implementation regression | Fix issues before snapshot updates |
