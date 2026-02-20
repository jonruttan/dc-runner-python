# Contributing

## Setup

```sh
make setup
```

## Required Checks

```sh
make verify
```

## Updating Pinned Snapshots

Global contracts:

```sh
make spec-sync TAG=<tag-or-ref> SOURCE=<path-or-url>
```

Runner-specific contracts:

```sh
make runner-spec-sync TAG=<tag-or-ref> SOURCE=<path-or-url>
```

Then run:

```sh
make verify
```

Commit updated lock files, manifests, and vendored snapshots together.
