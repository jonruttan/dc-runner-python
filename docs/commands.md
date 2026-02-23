# Commands

## Core

```sh
make setup
make lint
make typecheck
make smoke
make verify
make transition-gate
```

## Global Specs (`data-contracts`)

```sh
make spec-sync TAG=<tag-or-ref> SOURCE=<path-or-url>
make spec-sync-check
make compat-check
```

## Runner Specs (`data-contracts-library`)

```sh
make runner-spec-sync TAG=<tag-or-ref> SOURCE=<path-or-url>
make runner-spec-check
```

## Transition Refactor Gate

```sh
make transition-gate
```

Runs phase-transition checks and uses Rust adapter fallback when Python lane
compat checks are flaky during deep refactor work.
