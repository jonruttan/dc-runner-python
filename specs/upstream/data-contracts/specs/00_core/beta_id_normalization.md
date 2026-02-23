# Beta ID Normalization

This document records deterministic ID normalization used by canonical v1
surfaces.

## Rule

- Governance/library symbolic IDs use the `beta.*` namespace.
- Normalization is lexical and deterministic.
- Suffix structure, ordering, and separators are preserved.

## Examples

- `beta.scan`
- `beta.check_profile_text_file_config`
- `beta.root_runner_interface_subcommands_*`
- `beta.exports_as_*`

## Reference Integrity

- Check-set, prefix-map, traceability, fixture, and generated governance
  interface references use the normalized beta IDs.
