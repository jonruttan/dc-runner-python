# Current Spec Snapshot

Source of truth: spec.current

Spec-Version: 1
Date: 2026-02-18

## Canonical Model

- Executable fence: `yaml contract-spec`
- Executable case types: `contract.check`, `contract.export`, `contract.job`
- Assertion root: `contract`
- Assertion step shape: `contract.steps[].assert` (mapping or list of expression mappings)
- Assertion imports: `contract.imports` with per-step overrides at `contract.steps[].imports`
- Contract step metadata: `required` (default `true`), `priority` (default `1`), `severity` (default `1`)
- Hook root and events: `when.required|when.optional|when.fail|when.complete`
- Producer exports: `harness.exports`
- Consumer imports: `harness.use[*].symbols`
- Job metadata and dispatch: `harness.jobs` + `ops.job.dispatch`
- Bundle taxonomy: `bundle -> domains[] -> modules[] -> contracts[]` with canonical metadata
  names `bundle_version` and `maintainers`
- Runner sync task contract: required task IDs are `bundle-sync` and `bundle-sync-check`
- Project multi-bundle lock: root `bundles.lock.yaml` using `project_bundle_lock_v1`
- Implementation runner spec bundles: `dc-runner-*-specs` build patch overlays on
  canonical base bundles from `data-contracts-bundles` and publish
  implementation-specific `data-contract-bundle-*` assets

## Canonical Specs

- `/specs/01_schema/schema_v1.md`
- `/specs/02_contracts/index.md`
- `/specs/04_governance/index.md`
- `/specs/05_libraries/index.md`
- `external runner spec repository specs/index.md`

## Derived Docs

Generated references in `/docs/book/9*.md` are derived from canonical spec sources and must be regenerated when contracts or governance catalogs change.

## Runtime Profiling Snapshot

- `run_trace_v1` contract snapshot is defined in `/specs/01_schema/run_trace_v1.yaml`.
