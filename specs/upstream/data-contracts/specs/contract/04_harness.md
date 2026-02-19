# Harness Contract (v1)

## Dispatch

- Runner dispatches by case `type`.
- Harness receives parsed case and execution context.
- Harness runtime workflow is componentized and MUST use shared components:
  `build_execution_context`, `run_assertions_with_context`,
  `resolve_subject_for_target`.

## Entrypoint

For `type: cli.run`:

- `harness.entrypoint` MUST be provided by the spec.
- Portable conformance fixtures MUST provide `harness.entrypoint` explicitly.
- Implementations SHOULD provide a safe mode that disables hook entrypoints
  (for example `SPEC_RUNNER_SAFE_MODE=1`).
- Implementations SHOULD support a process-env allowlist control for `cli.run`
  executions (for example `SPEC_RUNNER_ENV_ALLOWLIST=K1,K2`).

Policy ids for these requirements are listed in
`specs/contract/policy_v1.yaml`.

## Canonical Targets

For `cli.run`:

- `stdout`
- `stderr`
- `stdout_path`
- `stdout_path_text`
- `chain_json`
- `context_json` (JSON subject profile envelope)

For `text.file`:

- `text`
- `chain_json`
- `context_json` (JSON subject profile envelope)

For `api.http`:

- `status`
- `headers`
- `body_text`
- `body_json`
- `cors_json`
- `steps_json`
- `chain_json`
- `context_json` (JSON subject profile envelope)

`api.http` auth/runtime profile:

- `harness.api_http.mode` (optional): `deterministic` (default) or `live`
  - `deterministic` forbids network `http(s)` fetches for request/token URLs
  - `live` allows network `http(s)` fetches
- `harness.api_http.scenario` (optional mapping):
  - `setup.command` / `teardown.command` for lifecycle shell commands
  - optional `setup.ready_probe` polling (`url`, `method`, expected status list,
    timeout/interval)
  - optional `cwd` / `env` for setup/teardown commands
  - `fail_fast` (default `true`)
- `harness.api_http.auth.oauth` (optional mapping):
  - `grant_type`: must be `client_credentials`
  - `token_url` (required)
  - `client_id_env` / `client_secret_env` (required): env var names only
  - `scope` / `audience` (optional)
  - `auth_style`: `basic` (default) or `body`
  - `token_field`: default `access_token`
  - `expires_field`: default `expires_in`
  - `refresh_skew_seconds`: default `30`

OAuth behavior:

- credentials are resolved from env references only (no inline secret fields)
- bearer token is injected as `Authorization: Bearer <token>` unless request
  headers already define `Authorization`
- `api.http` context metadata must not include raw secret/token values
- request CORS helper (`request.cors`) supports preflight and actual request
  checks through normalized `cors_json` projection
- scenario requests (`requests`) support `{{steps.<id>...}}` template lookups
  in `url`, header values, and `body_text`

Cross-spec chaining profile:

- all executable case types are chainable through `harness.chain`.
- executable case types MUST NOT use `harness.spec_lang.includes` for symbol
  loading; use `harness.chain` symbol exports/imports.
- `harness.chain.fail_fast` is optional and defaults to `true`.
- `harness.chain.steps` is required when `harness.chain` is present and must
  be non-empty.
- each step requires:
  - `id` (unique string)
  - `class` (`must`, `can`, `cannot`)
  - `ref` string in format `[path][#case_id]`
- producer symbol declarations are canonical at `harness.exports`.
- `harness.chain.steps[*].imports` and `harness.chain.steps[*].exports` are
  forbidden non-canonical locations.
- `allow_continue` is optional and defaults to `false`.
- `harness.chain.imports` is optional and declares explicit state imports:
  - `from` (required)
  - `names` (required)
  - `as` alias map (optional)
- imported local names and aliases must be unique and must not collide with
  reserved names (`subject`, `if`, `let`, `fn`, `call`, `var`).

Reference resolution:

- `#case_id` only: resolve exact case in current document.
- `path#case_id`: resolve exact case in referenced document.
- `path` only: execute all cases in referenced document in document order.
- relative `path` values resolve from current spec document directory.
- when using hash-only refs in YAML, quote them (for example `ref: "#CASE-1"`).
- top-level `chain` and type-specific `*.chain` aliases are forbidden; chain
  is declared only at `harness.chain`.

Cycle and recursion safety:

- direct self-reference is forbidden.
- indirect chain cycles are forbidden.
- recursive re-entry during execution is forbidden.

State interpolation:

- downstream `api.http` request fields support
  `{{chain.<step_id>.<export_name>...}}` template resolution in `url`, header
  values, and `body_text`.
- `chain_json` exposes case-scoped chain payload (`state`, `trace`, `imports`)
  for assertions across all executable harness types.

For `orchestration.run`:

- `result_json`
- `stdout`
- `stderr`
- `exit_code`
- `chain_json`
- `context_json` (JSON subject profile envelope)

For `docs.generate`:

- `result_json`
- `output_text`
- `chain_json`
- `context_json` (JSON subject profile envelope)

## Subject-Driven Assertion Contract

- Harnesses/adapters own target subject extraction and normalization.
- Assertion applicability is determined by subject availability/shape.
- Projected subjects consumed by spec-lang MUST be JSON values; native/runtime
  structures MUST be represented by JSON profile envelopes.
- External operators (`contain`, `regex`, `json_type`, `exists`) are authoring
  sugar that compile to `evaluate`-equivalent predicates.
- Runtime pass/fail decisions MUST execute compiled predicates through the
  spec-lang evaluator.

Subject profile envelope contract:

- `specs/contract/20_subject_profiles_v1.md`

## Spec-Lang Reuse

- `harness.spec_lang.includes` MAY provide ordered library docs/files
  containing `type: spec_lang.export` reusable function definitions.
- this include surface is for library authoring/composition; executable case
  symbol loading is chain-first.
- `harness.spec_lang.exports` MAY constrain visible imported symbols to an
  explicit allowlist.
- `harness.spec_lang.imports` MAY declare case-scoped imports using
  `from: std.<namespace>` or `from: ops.<namespace>` and `names: [...]` with
  optional `as` aliases.
- `when` MAY declare lifecycle hooks as non-empty expression lists:
  - `must`, `can`, `cannot`, `fail`, `complete`
  - non-canonical `harness.on` is forbidden
  - class hooks run after successful clause pass
  - `fail` runs once on first failure
  - `complete` runs after all clauses and class hooks pass
  - hook failures are runtime-fatal
- for `type: contract.job`, harness stores job metadata at `harness.jobs`:
  - `harness.jobs.<name>.helper` (required)
  - `harness.jobs.<name>.mode` (optional)
  - `harness.jobs.<name>.inputs` / `outputs` (optional mappings)
- Rust job spec pattern standardizes lifecycle diagnostics with hook jobs:
  - `harness.jobs.on_fail` + `when.fail -> ops.job.dispatch(on_fail)`
  - `harness.jobs.on_complete` + `when.complete -> ops.job.dispatch(on_complete)`
- non-canonical `harness.job` singular shape is forbidden.
- job execution is dispatched from `contract` expressions via
  `ops.job.dispatch`.

## Orchestration Tooling

- `type: orchestration.run` uses `harness.orchestration` for runner tool
  dispatch contracts.
- tool definitions are registry-backed per implementation:
  - `specs/governance/tools/python/tools_v1.yaml`
  - `specs/governance/tools/rust/tools_v1.yaml`
- `effect_symbol` naming MUST use deep-dot `ops.*` hierarchy:
  `ops.<segment>(.<segment>)+`
  (for example `ops.fs.file.read`, `ops.time.clock.now_utc`,
  `ops.proc.command.exec`).
- non-canonical underscore forms are forbidden.

## Docs Generation Harness

- `type: docs.generate` uses `harness.docs_generate` for spec-driven docs
  generation surfaces.
- `surface_id` MUST resolve to a declared docs generator surface in
  `specs/schema/docs_generator_registry_v1.yaml`.
- output behavior is explicit: `output_mode` is `markers` or `full_file`.
- marker mode writes only inside generated marker boundaries.
- template rendering uses moustache-core semantics and declared data sources
  (`json_file`, `yaml_file`, `generated_artifact`, `command_output`).

## Path Safety

- `cli.run` `harness.setup_files[*].path` MUST be relative and MUST resolve
  within the runner temp directory.
- spec-authored contract paths use virtual-root semantics:
  `/` means contract root (not OS root).
- root-relative values normalize to canonical `/...`.
- `text.file` `path` MUST resolve within contract root; `..` escapes are
  invalid.
- external references are `external://provider/id` and are deny-by-default
  unless explicitly enabled by capability + harness external ref policy.

## Trust Model

- Spec files are trusted inputs. `cli.run` executes commands/module entrypoints
  declared in spec data and harness config.
- Runner hook entrypoints (`hook_before` / `hook_after`) execute project code
  with the same process privileges as the test runner.
- Implementations MAY inherit process environment variables for `cli.run`.
  Operators MUST treat process environment as potentially exposed to the system
  under test and SHOULD avoid loading unrelated secrets in runner environments.
- Running specs from untrusted sources is out of scope for v1 and MUST be
  treated as unsafe.
