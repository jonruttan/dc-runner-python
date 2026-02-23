# Bundle Package Management Contract (v1)

Defines package-based bundle producer/consumer behavior for runner repositories
and projects installing multiple bundles.

## Purpose

- Replace snapshot-style spec sync workflows with bundle package pull + verify
  semantics.
- Keep package source immutable through release-asset URLs and checksums.
- Preserve deterministic runner-side materialization contracts.

## Canonical Librarian Repository

Canonical bundle manifests and release assets are owned by:

- `https://github.com/jonruttan/data-contracts-bundles`

`data-contracts` defines contracts and schemas for bundle behavior but is not
the canonical manifest source.

Shared reusable library and overlay sources are owned in:

- `https://github.com/jonruttan/data-contracts-library`

## Producer Responsibilities (`data-contracts-bundles`)

- Publish bundle package release assets:
  - `data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz`
  - `data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz.sha256`
  - `data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz.intoto.json`
- Ensure package payload contains:
  - resolved filesystem tree
  - `resolved_bundle_lock_v1.yaml`
  - `resolved_files.sha256`
- Scaffold bundles MUST also contain:
  - `scaffold/scaffold_manifest_v1.yaml`
  - `scaffold/files/**`
  - `scaffold/templates/**`
- Ensure package checksums are reproducible from published bytes.
- Derive package payload selection from canonical contract `assets[]`
  declarations only.
- Selector walk is deterministic and required:
  1. load module `contracts[]`
  2. read `assets[]`
  3. keep only static local refs
  4. normalize to repo-relative canonical paths
  5. materialize deterministic merged file set
- `artifacts[]` are semantic outputs only and are excluded from source payload
  selection.
- Store declaration provenance as digest metadata derived from selected
  declaration-driven paths.
- For scaffold bundles, declaration provenance MUST include scaffold manifest and
  all required materialization sources.

## Consumer Responsibilities (Projects and Runner Repositories)

Projects MUST pin bundle installs in root `bundles.lock.yaml` using:

- `/specs/01_schema/project_bundle_lock_v1.yaml`

Project scaffold commands MUST support canonical bundle host resolution:

- input: `bundle_id + bundle_version`
- host: `jonruttan/data-contracts-bundles` release assets
- tarball asset: `data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz`
- checksum sidecar: same asset name with `.sha256` suffix

External URL scaffold mode is optional and MUST be explicitly gated by a
caller opt-in flag.

Installers and runner wrappers MUST implement:

- `bundle-sync` / `install`: fetch package URLs, verify checksums, unpack each
  bundle into dedicated install directories, and verify
  `resolved_bundle_lock_v1.yaml`.
- `bundle-sync-check` / `install-check`: re-verify package checksums and
  materialized file manifest drift.
- `project scaffold`:
  - fetch tarball and `.sha256` sidecar in canonical mode
  - verify sidecar checksum against fetched tarball bytes
  - materialize root `bundles.lock.yaml`
  - install and check bundle payload integrity (`resolved_bundle_lock_v1.yaml`,
    `resolved_files.sha256`, and declaration digest verification)
  - load and apply `scaffold/scaffold_manifest_v1.yaml` entries deterministically
    to materialize project files

Multiple bundle entries are supported and MUST be install-isolated.
Install directory overlap is forbidden.

## Deterministic Resolution and Locking

- Bundle dependency resolution MUST be deterministic and hard-fail on cycles,
  missing dependencies, and conflicting file bytes.
- Resolved lock schema:
  `/specs/01_schema/resolved_bundle_lock_v1.yaml`
- Bundle manifest schema:
  `/specs/01_schema/bundle_manifest_v1.yaml`
- Implementation overlay schema:
  `/specs/01_schema/implementation_bundle_overlay_v1.yaml`
- Implementation build lock schema:
  `/specs/01_schema/implementation_bundle_build_lock_v1.yaml`
- Project lock schema:
  `/specs/01_schema/project_bundle_lock_v1.yaml`
- Scaffold manifest schema:
  `/specs/01_schema/scaffold_manifest_v1.yaml`
- Runner lock schema:
  `/specs/01_schema/runner_bundle_lock_v1.yaml`

`runner_bundle_lock_v1` is unsupported and retained only for normalization
compatibility.

Bundle manifest/lock files are package metadata, not semantic authority for
resource declarations. Canonical resource semantics are owned by
`data-contracts` schema and executable specs.

`bundle_manifest_v1` module `include_paths` and `exclude_paths` are not part of
canonical semantics.

## Bundle Governance Boundary

- Bundle/package governance is a package-contract concern and not part of the
  executable `contract-spec` suite top-level schema shape.
- Self-hosted tools may install their own governing bundle package (for
  example `data-contracts-bundler`) and run conformance/governance checks from
  that installed bundle content.

## Self-Bootstrap Pattern (One-Time Ad-Hoc)

For tools governed by their own bundle package, one ad-hoc bootstrap step is
allowed to solve first-install chicken-and-egg constraints:

- bootstrap lock input MUST be pinned and deterministic.
- bootstrap install MUST verify package checksums.
- bootstrap install MUST verify `resolved_bundle_lock_v1.yaml` and
  `resolved_files.sha256`.
- repeated ad-hoc bootstrap MUST fail unless an explicit force/reset path is
  provided.
- after successful bootstrap, standard `bundles.lock.yaml`-governed
  `install`/`install-check` behavior is required.

## Failure Behavior

Failure messages MUST be direct and actionable:

- missing release asset URL in runner lock
- missing root `bundles.lock.yaml` project lock
- duplicate bundle lock entries
- overlapping bundle install directories
- missing or malformed checksum file
- checksum mismatch between package bytes and lock/checksum metadata
- missing `resolved_bundle_lock_v1.yaml` in unpacked package
- local materialization drift vs `resolved_files.sha256`
- declaration/provenance digest mismatch between package metadata and resolved
  source spec declarations
- canonical release asset or checksum sidecar not found
- external URL requested without explicit opt-in

## Compatibility

- canonical bundle manifests are no longer sourced from local
  `/specs/bundles/*.yaml` in this repository.
- Runner task IDs `spec-sync` and `spec-sync-check` are not part of required
  build tool contract surface.
