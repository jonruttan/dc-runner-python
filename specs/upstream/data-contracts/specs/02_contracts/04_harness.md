# Harness Contract (v1)

## Dispatch

- Runner dispatches by suite-root `harness` mapping.
- Harness receives parsed suite/case data and execution context.
- Optional suite-root `adapters[]` provides concrete mechanism actions.
- Optional suite-root `services[]` provides contract-facing service composition
  (`exposes` + `bindings`) over adapter actions.
- `adapters[].type` is integration-only in v1 (`io.fs`, `io.http`,
  `io.system`, `io.mysql`, `io.docs`); orchestration categories (`assert.check`,
  `assert.export`, `ops.job`) are invalid as service types.
- `adapters[].actions[].profile` is a profile token validated per integration type
  (`read.text`, `request.http`, `exec.command`, `generate.docs`, etc.).
- `adapters[].actions[].imports` supports canonical list mappings (`names` + optional `as`)
  and compact list[string] aliases.
- Contract-scoped `contracts.clauses[].bindings` connects contracts to services and
  artifact channels using `contracts.clauses[].bindings.defaults + contracts.clauses[].bindings.rows[]`.
- Binding I/O supports canonical mapping rows and compact endpoint aliases:
  - `outputs`: `{to, as?, path?}`
  - `inputs`: `{from, as?}`
- clause/predicate imports support canonical rows (`{from, names, service?, as?}`)
  and supported compact aliases.
- Harness runtime workflow is componentized and MUST use shared components:
  `build_execution_context`, `run_assertions_with_context`,
  `resolve_subject_for_target`.

Suite-root external references:

- executable suites MAY declare `assets[]` and `artifacts[]`
  to model artifact references external to per-contract harness/assertion
  blocks.
- root `exports[]` is reserved for function symbol exports only.
- `assets[].ref` and `artifacts[].ref` template expressions use
  moustache (`{{...}}`) syntax and resolve from suite context only.
- service runtime payload transport MUST use artifact ids declared in
  `assets[]` and `artifacts[]` through `contracts.clauses[].bindings.rows[]` mappings.
- services MUST NOT reference external locations directly in
  `adapters[].actions[].config`; direct locator keys (`path`, `url`, `token_url`,
  `template_path`, `output_path`, `ref`) are invalid.
- service config locators MUST be routed via artifact IDs using
  profile-specific `*_asset_id` fields (for example
  `source_asset_id`, `artifact_id`, `token_asset_id`,
  `template_asset_id`, `output_artifact_id`, `use[].asset_id`).
- services/harnesses define execution capabilities only; they do not implicitly
  inject predicate symbols.
- core runner orchestration must not embed integration-specific client
  libraries (for example HTTP clients); integration behavior is owned by service
  implementations.
- service implementations may be packaged built-in or as runtime plugins with
  identical observable behavior.
- runtime plugin lifecycle and lock/signature requirements are defined in
  `/specs/02_contracts/35_service_plugin_runtime.md`.
- artifact symbols are available to predicates only when explicitly declared
  and wired.
- when `contracts.clauses[].bindings.rows[]` or `from: service` imports are present,
  `services` and `adapters` MUST be declared and valid.
- binding defaults are additive only: explicit row values override defaults.
- `service` and `import` are effective-required after defaults merge.
- scan-style harness config must use explicit structured keys:
  - `harness.config.root`
  - `harness.config.check.profile`
  - `harness.config.check.config.check`
  - `harness.config.use[]` (`ref`, `as`, `symbols`)
- documentation metadata uses `docs[]` entries (not singular `doc`) at suite,
  contract, artifacts import/export, and root function export surfaces.
- docs entry and docs-owner ids are optional metadata keys; when omitted,
  runtimes may emit deterministic report labels only for diagnostics.
- report labels are not schema identity and must not be accepted as reference
  targets.
- terminology:
  - accepted input forms: parser-supported canonical surfaces
  - preferred authoring form: canonical mappings / defaults+rows
  - canonical normalized form: deterministic post-normalization runtime shape

## Entrypoint

For `harness.type: unit.test` with `adapters[].actions[].profile: exec.command`:

- `adapters[].actions[].config.entrypoint` MUST be provided by the spec.
- Portable conformance fixtures MUST provide explicit entrypoint config.
- Implementations SHOULD provide a safe mode that disables hook entrypoints
  (for example `SPEC_RUNNER_SAFE_MODE=1`).
- Implementations SHOULD support a process-env allowlist control for `exec.command`
  executions (for example `SPEC_RUNNER_ENV_ALLOWLIST=K1,K2`).

Policy ids for these requirements are listed in
`specs/02_contracts/policy_v1.yaml`.

## Canonical Targets

For `exec.command`:

- `stdout`
- `stderr`
- `stdout_path`
- `stdout_path_text`
- `chain_json`
- `context_json` (JSON subject profile envelope)

For `read.text`:

- `text`
- `chain_json`
- `context_json` (JSON subject profile envelope)

For `request.http`:

- `status`
- `headers`
- `body_text`
- `body_json`
- `cors_json`
- `steps_json`
- `chain_json`
- `context_json` (JSON subject profile envelope)

`request.http` auth/runtime profile:

- `adapters[].actions[].config.api_http.mode` (optional): `deterministic` (default) or `live`
  - `deterministic` forbids network `http(s)` fetches for request/token URLs
  - `live` allows network `http(s)` fetches
- `adapters[].actions[].config.api_http.scenario` (optional mapping):
  - `setup.command` / `teardown.command` for lifecycle shell commands
  - optional `setup.ready_probe` polling (`url`, `method`, expected status list,
    timeout/interval)
  - optional `cwd` / `env` for setup/teardown commands
  - `fail_fast` (default `true`)
- `adapters[].actions[].config.api_http.auth.oauth` (optional mapping):
  - `grant_type`: must be `client_credentials`
  - `token_asset_id` (required): artifacts import id containing token endpoint
    locator payload
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
- `request.http` context metadata must not include raw secret/token values
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
  - `required` (bool, optional, default `true`)
  - `priority` (int, optional, default `1`, must be `>=1`)
  - `severity` (int, optional, default `1`, must be `>=1`)
  - `purpose` (string, optional, non-empty when provided)
  - `ref` string in format `[path][#case_id]`
- producer symbol declarations are canonical at suite-root `exports[]` using
  `from: assert.function`.
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

Cycle and recursion safety:

- direct self-reference is forbidden.
- indirect chain cycles are forbidden.
- recursive re-entry during execution is forbidden.

State interpolation:

- downstream `request.http` request fields support
  `{{chain.<step_id>.<export_name>...}}` template resolution in `url`, header
  values, and `body_text`.
- `chain_json` exposes case-scoped chain payload (`state`, `trace`, `imports`)
  for assertions across all executable harness types.

For orchestration runtime metadata:

- `result_json`
- `stdout`
- `stderr`
- `exit_code`
- `chain_json`
- `context_json` (JSON subject profile envelope)

For `generate.docs`:

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

- `specs/02_contracts/20_subject_profiles_v1.md`

## Spec-Lang Reuse

- `clauses.config.spec_lang.includes` MAY provide ordered library docs/files
  containing `type: spec_lang.export` reusable function definitions.
- this include surface is for library authoring/composition; executable case
  symbol loading is chain-first.
- `harness.spec_lang.exports` MAY constrain visible imported symbols to an
  explicit allowlist.
- `harness.spec_lang.imports` MAY declare case-scoped imports using
  `from: std.<namespace>` or `from: ops.<namespace>` and `names: [...]` with
  optional `as` aliases.
- `when` MAY declare lifecycle hooks as non-empty expression lists:
  - `required`, `optional`, `fail`, `complete`
  - `required` runs after successful required-step evaluation
  - `optional` runs after successful optional-step evaluation
  - `fail` runs once on first failure
  - `complete` runs after all steps and hooks pass
  - hook failures are runtime-fatal
- for `harness: job`, metadata is stored at `clauses.config.jobs[]`:
  - `clauses.config.jobs[].id` (required, unique)
  - `clauses.config.jobs[].helper` (required)
  - `clauses.config.jobs[].mode` (optional)
  - `clauses.config.jobs[].inputs` / `outputs` (optional mappings)
- Rust job spec pattern standardizes lifecycle diagnostics with hook jobs:
  - job id `on_fail` + `when.fail -> ops.job.dispatch(on_fail)`
  - job id `on_complete` + `when.complete -> ops.job.dispatch(on_complete)`
- job execution is dispatched from `clauses` expressions via
  `ops.job.dispatch`.

## Orchestration Tooling

- orchestration dispatch uses `clauses.config.orchestration` for runner tool
  dispatch contracts.
- tool definitions are registry-backed per implementation:
  - `specs/04_governance/tools/python/tools_v1.yaml`
  - `specs/04_governance/tools/rust/tools_v1.yaml`
- `effect_symbol` naming MUST use deep-dot `ops.*` hierarchy:
  `ops.<segment>(.<segment>)+`
  (for example `ops.fs.file.read`, `ops.time.clock.now_utc`,
  `ops.proc.command.exec`).

## Docs Generation Harness

- docs generation uses `clauses.config.docs_generate` for spec-driven docs
  generation surfaces.
- `surface_id` MUST resolve to a declared docs generator surface in
  `specs/01_schema/docs_generator_registry_v1.yaml`.
- output behavior is explicit: `output_mode` is `markers` or `full_file`.
- marker mode writes only inside generated marker boundaries.
- template rendering uses moustache-core semantics and declared data sources
  (`json_file`, `yaml_file`, `generated_artifact`, `command_output`).

## Path Safety

- `exec.command` `harness.setup_files[*].path` MUST be relative and MUST resolve
  within the runner temp directory.
- spec-authored contract paths use virtual-root semantics:
  `/` means contract root (not OS root).
- root-relative values normalize to canonical `/...`.
- `read.text` locator payloads MUST be declared under `assets[]` and
  referenced through `adapters[].actions[].config.source_asset_id`.
- external references are `external://provider/id` and are deny-by-default
  unless explicitly enabled by capability + harness external ref policy.

## Trust Model

- Spec files are trusted inputs. `exec.command` executes commands/module entrypoints
  declared in spec data and harness config.
- Runner hook entrypoints (`hook_before` / `hook_after`) execute project code
  with the same process privileges as the test runner.
- Implementations MAY inherit process environment variables for `exec.command`.
  Operators MUST treat process environment as potentially exposed to the system
  under test and SHOULD avoid loading unrelated secrets in runner environments.
- Running specs from untrusted sources is out of scope for v1 and MUST be
  treated as unsafe.
