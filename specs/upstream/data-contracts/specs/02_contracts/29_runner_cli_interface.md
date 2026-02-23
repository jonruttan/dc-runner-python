# Runner CLI Interface Contract (v1)

Defines the portable CLI surface shared by runner implementations and consumed
by the control-plane conformance layer.

## Scope

This contract specifies only implementation-agnostic runner CLI behavior.
Runtime-specific or implementation-specific subcommands remain runner-owned.
Runner-owned CLI behavior specs are maintained in external runner spec
repositories, not in canonical schema trees.
Command behavior is resolved from spec-defined command entrypoints, not shell
wrappers.

## MUST Surface

Runner CLIs MUST provide deterministic behavior for:

- `dc-runner --help`
- `dc-runner conformance`
- `dc-runner governance`
- `dc-runner critical-gate`
- `dc-runner docs-generate-check`
- `dc-runner contract-spec-format --check <paths...>`
- `dc-runner contract-spec-format --write <paths...>`
- `dc-runner project scaffold --project-root <path> --bundle-id <id> --bundle-version <semver> [--runner <rust|python|php>]`
- `dc-runner project scaffold --project-root <path> --bundle-id <id> --bundle-version <semver> [--runner <rust|python|php>] [--var <key=value>]... [--overwrite]`
- unknown command handling with non-zero exit code
- structured status output mode (`--json` or equivalent capability)

## MAY Surface

Runner CLIs MAY provide:

- implementation-specific helper subcommands
- additional diagnostics modes
- additional output formats beyond the structured mode
- external scaffold source override:
  - `dc-runner project scaffold --project-root <path> --bundle-url <url> --sha256 <hex> --allow-external`

## Capability Model

Portable required behavior is represented as required commands and output
contract keys in `/specs/01_schema/runner_cli_contract_v1.yaml`.

`contract-spec-format` contract:

- processes Markdown `*.spec.md` files containing fenced `yaml contract-spec`
  blocks
- applies only to `spec_version: 1` blocks
- `--check` is read-only and exits non-zero when canonical order is found
- `--write` rewrites canonical v1 block key order in place
- non-v1 blocks are skipped (no rewrite)

Canonical executable case payload shape for formatting and execution is
`spec_version/schema_ref/harness/contracts.clauses[].asserts.checks[]`.

Implementation-specific additions MUST be capability-gated and MUST NOT weaken
the required portable command semantics.

## Entrypoint Resolution

Command-to-profile mapping source of truth:

- `/specs/04_governance/runner_entrypoints_v1.yaml`

Schema:

- `/specs/01_schema/runner_command_entrypoints_v1.yaml`

For canonical command entrypoints, `dc-runner` MUST resolve command id to
`/specs/governance/check_sets_v1.yaml` profile and enforce declared artifact
and exit-code contracts.

## Scaffold Source Contract

- Canonical scaffold source is `jonruttan/data-contracts-bundles` release assets.
- Canonical mode is bundle-identity based (`bundle_id` + `bundle_version`), not
  raw URL based.
- External URL mode is opt-in only and MUST require explicit
  `--allow-external`.
- Scaffold MUST verify bundle integrity before install and emit deterministic
  scaffold artifacts under `/.artifacts/`.
- Scaffold materialization MUST be driven by
  `/specs/01_schema/scaffold_manifest_v1.yaml` bundled as
  `scaffold/scaffold_manifest_v1.yaml`.
- Canonical scaffold bundle IDs for language scaffolding are:
  - `data-contracts-lang-project-scaffold`
  - `data-contracts-lang-rust-project-scaffold`
