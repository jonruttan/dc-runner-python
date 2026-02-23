# Bundler CLI Contract (v1)

## Commands

- `bundle bootstrap`
  - one-time ad-hoc bootstrap for self-governed tool installation
  - bootstrap lock MUST contain exactly one bundle entry
  - bootstrap bundle id MUST equal `data-contracts-bundler`
  - fails if `.bundler/bootstrap.state.json` exists unless `--force-bootstrap` is set
- `bundle install`
  - installs all bundles from pinned lock
  - verifies package sha256 against lock `source.sha256`
  - verifies unpacked `resolved_bundle_lock_v1.yaml` exists
  - verifies unpacked `resolved_files.sha256` matches bytes on disk
  - for scaffold bundles, verifies `scaffold_manifest_v1.yaml` and required materialization source paths
- `bundle check`
  - re-verifies installed bundles and drift against lock + resolved file manifest

## Post-Bootstrap Invariant

Normal install/check flows MUST use pinned lock metadata only and MUST NOT accept unguided ad-hoc source inputs.

## Error Contract

Errors MUST be direct and actionable, including:

- invalid bootstrap lock shape
- wrong bootstrap bundle id
- checksum mismatch
- missing resolved lock
- missing or invalid resolved file manifest
- install directory overlap
