# Runner Implementation Spec Bundles Contract (v1)

Defines how implementation-specific runner spec bundles are produced as
deterministic overlays on top of canonical base bundles.

## Canonical Source Model

- Base runner bundle manifests and packages remain canonical in:
  `https://github.com/jonruttan/data-contracts-bundles`
- Reusable runner behavior overlays and shared reusable libraries are owned in:
  - `https://github.com/jonruttan/data-contracts-library`

## Overlay Semantics

Implementation repositories MUST define overlay intent using:

- `/specs/01_schema/implementation_bundle_overlay_v1.yaml`

Reusable runner behavior specs in `data-contracts-library` MUST keep
executable `.spec.md` cases in canonical v1 suite shape so overlay consumers
can parse and validate them deterministically.
Canonical schema docs in `data-contracts` must reference reusable-runner trees
through explicit external repository paths only.
Runner-side shell tooling must remain wrapper-only around runner command/spec
surfaces for deterministic cross-repo behavior.

Overlay operations are patch-based and file-scoped:

- `overlay.delete_paths[]`
- `overlay.add_files[]`
- `overlay.replace_files[]`

Line-level patch languages are out of scope for v1.
Full copied canonical trees are not the normative model.

## Deterministic Build Contract

Implementation spec repositories SHOULD expose bundle tasks:

- `build-impl`
- `package-impl`
- `package-check`

Implementation bundle build flow MUST:

1. Download pinned base package from `base_bundle.source.asset_url`.
2. Verify package bytes against `base_bundle.source.sha256`.
3. Unpack base package.
4. Apply overlay operations in deterministic order:
   - delete paths sorted lexicographically
   - add/replace files sorted by target path
5. Recompute `resolved_files.sha256`.
6. Emit:
   - `resolved_bundle_lock_v1.yaml`
   - `implementation_bundle_build_lock_v1.yaml`
7. Emit declaration provenance digest derived from resolved canonical
   `assets[]` / `artifacts[]` declarations referenced by bundled specs.

Build lock schema:

- `/specs/01_schema/implementation_bundle_build_lock_v1.yaml`

## Packaging and Release Assets

Implementation-specific packages MUST use canonical naming:

- `data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz`
- `data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz.sha256`
- `data-contract-bundle-{bundle_id}-v{bundle_version}.tar.gz.intoto.json`

Reusable runner behavior and overlay bundle sources are published from
`data-contracts-library` and packaged in `data-contracts-bundles`.

## Project Consumption

Projects consume implementation bundles through root `bundles.lock.yaml` using:

- `/specs/01_schema/project_bundle_lock_v1.yaml`

Implementation bundles SHOULD be pinned as `role: additional` entries and MUST
use dedicated `install_dir` paths that do not overlap with other bundle
install directories.

Language scaffold bundles published in `data-contracts-bundles` are canonical
project bootstrap sources:

- `data-contracts-lang-project-scaffold`
- `data-contracts-lang-rust-project-scaffold`

When a scaffold bundle is consumed through `project scaffold`, runner
materialization MUST be driven by `scaffold/scaffold_manifest_v1.yaml`.

## Failure Behavior

Failure messages MUST be direct and actionable for:

- missing overlay source file
- replace/delete target path missing in materialized base tree
- base package download failure
- base package checksum mismatch
- missing `resolved_bundle_lock_v1.yaml` in packaged output
- missing or mismatched `resolved_files.sha256`
- declaration/provenance digest mismatch during package verify/unbundle
