# Architecture

## System Boundary

Text boundary model:

- Data Contracts upstream (`https://github.com/jonruttan/data-contracts`):
  canonical contracts/specs/schemas/governance definitions.
- This repository (`dc-runner-python`): Python runner implementation and
  compatibility verification logic.

## Artifact Ownership

Local runner-owned artifacts:

- `/runner_adapter.sh`
- `/spec_runner/**`
- `/specs/impl/python/index.md` (pointer only)
- `/scripts/sync_data_contracts_specs.sh`
- `/scripts/verify_upstream_compat.sh`
- `/scripts/sync_runner_specs.sh`
- `/scripts/verify_runner_specs.sh`

Pinned upstream compatibility artifacts:

- `/specs/upstream/data_contracts_lock_v1.yaml`
- `/specs/upstream/data-contracts.manifest.sha256`
- `/specs/upstream/data-contracts/**`
- `/specs/upstream/dc_runner_spec_lock_v1.yaml`
- `/specs/upstream/dc-runner-spec.manifest.sha256`
- `/specs/upstream/dc-runner-spec/specs/impl/python/**`

## Execution Model

Runtime flow:

1. Caller invokes `/runner_adapter.sh <subcommand>`.
2. Adapter dispatches to Python command entrypoints.
3. Python runner performs checks/contracts work.
4. Process returns stable exit semantics.

## Compatibility Verification Model

The compatibility model is lock-driven and deterministic:

1. Lock file records upstream repo/tag-or-ref/commit and integrity metadata.
2. Vendored snapshot holds curated upstream compatibility surface.
3. Manifest tracks deterministic per-file checksums.
4. Verification scripts enforce lock/snapshot/manifest coherence and adapter
   command compatibility.

## Change Impact Matrix

- Python runtime behavior changes:
  - update implementation
  - run `/make verify`
  - update docs if interface/operations changed
- Upstream compatibility version bump:
  - run `/make spec-sync TAG=<tag-or-ref> SOURCE=<source>`
  - run `/make verify`
  - commit lock + snapshot + manifest
- Runner interface or command semantics changes:
  - preserve compatibility guarantees, or treat as explicit breaking change
  - update `/README.md`, `/CONTRIBUTING.md`, and command docs
