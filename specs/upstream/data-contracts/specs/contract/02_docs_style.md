# Docs Style Contract

Source of truth: spec.contract.docs_style

## Style Rules

- Use canonical terminology: `contract-spec`, `contract`, `asserts`, `MUST|MAY|MUST_NOT`, `when.must|when.may|when.must_not|when.fail|when.complete`.
- Link to absolute virtual-root paths inside the repo (for example `/specs/schema/schema_v1.md`).
- Keep executable examples in fenced `yaml contract-spec` blocks.
- Keep ownership and generated/derived status explicit in index pages.

## Drift Rules

- Broken links are invalid.
- Generated docs drift is invalid.
- Stale legacy terms in active docs are invalid.
