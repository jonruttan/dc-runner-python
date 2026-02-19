# Release

## Release Preconditions

Before tagging a release:

```sh
make verify
```

## Version Bump Flow

1. Update package/release metadata in `/pyproject.toml`.
2. Run:

```sh
make verify
```

3. Update changelog/release notes for user-visible changes.
4. Commit release changes.

## Tagging Policy

Use semantic tags:

- `vX.Y.Z`

Example:

```sh
git tag v0.2.0
git push origin v0.2.0
```

## Automated Release Artifacts

Workflow: `/.github/workflows/release.yml`

Trigger:

- push tag matching `v*`
- optional manual `workflow_dispatch`

Published assets:

- Python source distribution (`sdist`)
- Python wheel (`wheel`)
- per-file `.sha256` checksums

## Data Contracts Coordination Note

When Data Contracts compatibility version changes:

1. update pinned upstream snapshot (`/make spec-sync`)
2. verify compatibility (`/make verify`)
3. include lock/manifest/snapshot diff in release review

## Post-Release Validation

After push/tag:

1. Confirm CI and Release workflows are green for the tag.
2. Confirm release tag points at intended commit.
3. Confirm wheel/sdist and checksum files are attached.
4. Confirm compatibility checks pass from a clean checkout.
