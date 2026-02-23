# Contract Set Resolution Contract (v1)

Defines deterministic bundle dependency resolution for runner-facing spec pulls.

Canonical bundle taxonomy terms are defined in
`/specs/02_contracts/32_contract_bundle_taxonomy.md`.

## Canonical Unit

- Consumers MUST request one root `contract_set_id`.
- Dependency chaining is internal to resolution.
- Consumers MUST NOT compose multiple sets manually.

## Contract Set Manifest Shape

Each contract set manifest MUST declare:

- `contract_set_id` (string, unique in repository scope)
- `version` (integer)
- `depends_on` (list[string] of `contract_set_id`)
- `dependency_mode` (`required` or `optional`, default `required`)
- `include_paths` (non-empty list[path/glob], repo-relative)
- `exclude_paths` (optional list[path/glob], repo-relative)
- `applies_to_runners` (optional list: `python`, `php`, `rust`)

## Resolver Interface

Canonical resolver command contract:

- `bundle resolve --runner <runner> --root <bundle_id> --out <dir>`

Resolver output MUST materialize:

- resolved filesystem tree under `<dir>`
- `resolved_contract_set_lock_v1.yaml`
- deterministic file manifest (`resolved_files.sha256`)

No large JSON bundle artifact is required.

## Deterministic Resolution Rules

1. Build dependency DAG from `depends_on`.
2. Hard-fail on:
   - missing dependency
   - cycle
   - duplicate `contract_set_id`
   - invalid include path/glob
3. Topological ordering MUST use deterministic tie-break by lexicographic
   `contract_set_id`.
4. File merge semantics:
   - same output path with different bytes: hard-fail
   - same output path with same bytes: allowed
5. Lock file MUST include:
   - source repo/ref/commit
   - root contract set id
   - resolved order
   - integrity (`file_count`, manifest hash, manifest-set hash)

## Runner Compatibility

- Runner CLI and exit semantics remain stable.
- Minor help/output formatting cleanup is allowed.
- Resolver adoption MUST NOT introduce command/flag/exit-code drift in runner
  public interfaces.
