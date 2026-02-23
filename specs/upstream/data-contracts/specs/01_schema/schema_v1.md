# Spec-Test Schema (v1)

This schema defines the stable shape of executable spec tests embedded in
Markdown files selected by case-file pattern (default `*.spec.md`) as fenced blocks:

```text
```yaml contract-spec
...
```

Related docs/reference schemas:

- `specs/01_schema/docs_schema_v1.md`
- `specs/01_schema/reference_manifest_v1.md`
- `specs/01_schema/objective_metrics_schema_v1.md`
- `specs/01_schema/docs_generator_registry_v1.yaml`
- `specs/01_schema/docs_layout_profile_v1.yaml`
- `specs/01_schema/runner_api_catalog_v1.yaml`
- `specs/01_schema/harness_type_catalog_v1.yaml`
- `specs/01_schema/spec_lang_builtin_catalog_v1.yaml`
- `specs/01_schema/spec_lang_stdlib_profile_v1.yaml`
- `specs/01_schema/subject_profiles_v1.yaml`
- `specs/01_schema/run_trace_v1.yaml`
- `specs/01_schema/orchestration_result_v1.yaml`
- `specs/01_schema/registry_schema_v1.yaml`
- `specs/01_schema/registry/v1/*.yaml`
- `specs/02_contracts/19_spec_lang_stdlib_profile_v1.md`
- `specs/02_contracts/20_subject_profiles_v1.md`
- `specs/02_contracts/21_schema_registry_contract.md`
- `specs/02_contracts/24_runtime_profiling_contract.md`
```

## Suite Fields

- Machine source of truth for case-shape constraints lives in
  `specs/01_schema/registry/v1/*.yaml`; this document includes a generated
  registry snapshot section.

- `spec_version` (int, required): schema major used by this suite
- `schema_ref` (string, required): canonical virtual-root schema path
- `contracts` (mapping, required): contains `contracts.clauses[]` (non-empty list)
- `artifacts` (list, optional): suite-level artifact reference declarations
  - `id` (string, required)
  - `ref` (string, required): supports moustache template expressions (`{{...}}`)
    resolved from suite context
  - `direction` (string, required): `input|output|bidirectional`
  - `type` (string, optional): expected MIME type for resolved `ref`
  - `inputs` (mapping, optional)
  - `outputs` (mapping, optional)
  - `options` (mapping, optional)
  - `docs` (list, optional): documentation metadata entries
- `exports` (list, optional): function export declarations only
  - `exports[].as` (string, required): exported function symbol name
  - `exports[].from` (string, required): must be `assert.function`
  - `exports[].path` (string, required): producer function body path
  - `exports[].params` (list, optional): ordered parameter names
  - `exports[].required` (bool, optional): export requirement flag
  - `exports[].docs` (list, optional): function documentation metadata entries
- `domain` (string, optional): suite-level domain hint
- `title` (string, optional): suite-level label
- `purpose` (string, optional): suite-level description
- `docs` (list, optional): suite-level documentation metadata entries
  - required entry keys: `summary`, `audience`, `status`
  - `docs[].audience` enum: `operator|integrator|implementer|maintainer|governance|reviewer|auditor`
  - `docs[].audience` default: `implementer`
  - `id` is optional metadata; when omitted, runners may emit deterministic
    report labels only (not schema/reference identity)
  - optional entry keys: `description`, `type`, `since`, `updated_at`, `tags`, `owners`, `links`, `examples`
  - `docs[].type` enum: `overview|reference|howto|policy|contract|changelog`
  - explicit `docs[].id` values MUST be unique within each containing `docs[]` array scope

Bundle/package management is not part of `contract-spec` suite shape in v1.
Bundle taxonomy, lock, and package semantics are defined at package-contract
level in:

- `specs/02_contracts/32_contract_bundle_taxonomy.md`
- `specs/02_contracts/33_bundle_package_management.md`
- `specs/02_contracts/34_runner_implementation_spec_bundles.md`
- `specs/01_schema/bundle_manifest_v1.yaml`
- `specs/01_schema/resolved_bundle_lock_v1.yaml`
- `specs/01_schema/project_bundle_lock_v1.yaml`
- `specs/01_schema/implementation_bundle_overlay_v1.yaml`
- `specs/01_schema/implementation_bundle_build_lock_v1.yaml`

## v1 Canonical Key Order (Formatter Scope)

`contract-spec-format` v1 scope is intentionally narrow:

- suite root mapping keys
- each `contracts.clauses[]` mapping item

No recursive nested-map sorting and no array-item reordering are performed.

Suite root canonical order:

1. `spec_version`
2. `schema_ref`
3. `title`
4. `purpose`
5. `docs`
6. `domain`
7. `harness`
8. `services`
9. `artifacts`
10. `exports`
11. `contracts`

`contracts.clauses[]` canonical order:

1. `id`
2. `title`
3. `purpose`
4. `docs`
5. `domain`
6. `expect`
7. `requires`
8. `bindings`
9. `asserts`
10. `library`
11. `when`

Ordering rules:

- known keys are emitted in canonical order
- unknown keys are preserved after known keys in stable original order

Alias grammar source of truth:

- `/specs/01_schema/registry/v1/core.yaml and /specs/01_schema/registry/v1/assertions.yaml` defines compact/short alias
  grammars, normalization targets, mixed-form rules, and collision/failure
  contracts.
- core/assertions registries enumerate canonical fields and accepted compact
  aliases for v1 surfaces.
- list item order is preserved as-authored

Terminology contract (uniform across v1 docs/registry/policy):

- accepted input forms: parser-supported authoring shapes
- preferred authoring form: style guidance for low-overhead authoring
- canonical normalized form: deterministic internal row/map shape after
  alias/default normalization and before validation/runtime execution

Each `contracts.clauses[]` item:

- `id` (string, required): stable identifier like `CK-CLI-001`
- `asserts` (mapping, required)
- `title`/`purpose`/`domain` (optional overrides)
- `expect`/`requires`/`when` (optional)
- `contracts.clauses[].bindings` (mapping, optional): contract-local service
  binding declarations
  - mapping form (preferred compaction):
    `contracts.clauses[].bindings.defaults` + `contracts.clauses[].bindings.rows[]`
  - defaults keys (optional): `service`, `import`, `mode`, `predicates`
  - row keys: `id`, optional `service`, optional `import`, `inputs`, `outputs`,
    `predicates`, `mode`
  - effective row = shallow merge(defaults, row), row overrides defaults

Suite runtime surfaces:

- `harness` (mapping, required): suite orchestration surface
  - `harness.type` (string, required)
  - `harness.profile` (string, required)
  - `harness.config` (mapping, optional)
  - scan-style structured config keys:
    - `harness.config.root` (string, optional)
    - `harness.config.check.profile` (string, optional)
    - `harness.config.check.config.check` (string, optional)
    - `harness.config.use[]` (`ref`, `as`, `symbols`) (optional)
- `services` (list, optional): suite service type blocks
  - `adapters[].type` (string, required): service type token resolved by
    `/specs/01_schema/service_contract_catalog_v1.yaml` (for example `io.http`)
  - `adapters[].defaults` (mapping, optional): per-type defaults merged into each
    `adapters[].actions[]` row
  - `adapters[].actions` (list, required): non-empty concrete service instance rows
  - `adapters[].actions[].id` (string, required): concrete service instance id used by
    `contracts.clauses[].bindings` and `from: service` imports
  - `adapters[].actions[].profile` (string, optional): effective mode token
  - `adapters[].actions[].direction` (string, optional): `input|output|bidirectional`
  - `adapters[].actions[].config` (mapping, optional): service config values that
    reference external locations MUST use artifact-id fields (`*_asset_id`)
    and must not embed direct locators
  - `adapters[].actions[].imports` (list, optional): canonical mapping rows
    (`names`, optional `as`)
  - effective entry = shallow merge(`adapters[].defaults`, `adapters[].actions[]` row),
    with row keys overriding defaults
  - service implementations may be built-in or runtime-loaded plugins; suite
    authoring shape is unchanged
  - runtime plugin contracts:
    - `/specs/01_schema/service_plugin_manifest_v1.yaml`
    - `/specs/01_schema/service_plugin_lock_v1.yaml`
Parser behavior:

- discovery scans files matching case-file pattern (default `*.spec.md`) in
  the provided directory (non-recursive)
- default discovery is Markdown-only (`*.spec.md`)
- runners MAY opt in additional external case formats via explicit format
  selection (`yaml`, `json`)
- canonical executable spec trees (`specs/03_conformance/cases`,
  `specs/04_governance/cases`, `external runner spec repository specs`) are markdown-only and must
  not include runnable `.spec.yaml`/`.spec.yml`/`.spec.json` files
- fence extraction accepts Markdown fences using either backticks or tildes
  (3+), with info tokens including `contract-spec` and `yaml`/`yml`
- closing fences must use the same fence character and at least the opener
  length
- `contracts` is required and must be non-empty
- `spec_version` is required
- `schema_ref` is required
- each `contracts.clauses[]` item requires `id`
- suite `harness` mapping is required
- suite `services` is optional
- when `services` is present, `services[]` must be non-empty
- `schema_ref` MUST resolve in `/specs/01_schema/schema_catalog_v1.yaml`
- `spec_version` MUST match the schema major encoded by `schema_ref`
- `assets[].ref` and `artifacts[].ref` MUST be strings
- `assets[].ref` and `artifacts[].ref` template expressions
  use moustache syntax and resolve from suite context only
- unresolved asset/artifact `ref` template
  expressions are schema/runtime failures
- root `exports[]` is function-only:
  - `exports[].from` MUST be `assert.function`
  - `exports[].mode` is invalid
  - `exports[].id` is invalid
  - `exports[].ref` is invalid
- `contracts.clauses[].asserts.checks[].id` is required
- unknown `adapters[].type` MUST hard-fail during schema validation
- invalid `adapters[].actions[].direction` MUST hard-fail during schema validation
- service-specific integration behavior (for example HTTP client operations) is
  implementation-owned by resolved service implementations, not core runner
  orchestration logic
- runtime-loaded service implementations MUST pass lock + digest + signature
  verification before invocation
- `adapters[].actions[].imports` accepts canonical list[mapping] rows and compact
  list[string] aliases
- compact `adapters[].actions[].imports` names MUST be unique per adapter action
  and valid for resolved `adapters[].type/profile` in
  `/specs/01_schema/service_contract_catalog_v1.yaml`
- if any contract declares `contracts.clauses[].bindings.rows[]`, `services` MUST be present and valid
- if any `asserts.imports[]` or `asserts.checks[].imports[]` item uses
  `from: service`, `services` MUST be present and valid
- clause/predicate bare-string import rows (for example `- pipe_identity`) are
  compact service aliases normalized to
  `{from: service, names:[pipe_identity], service:<resolved>}`
- `<resolved>` service id for clause/predicate bare-string rows MUST come from
  `contracts.clauses[].bindings.defaults.service`; missing/empty defaults service is
  schema failure
- clause/predicate bare-string rows with unknown resolved service id are schema
  failures
- clause/predicate bare-string rows with import names not supported by resolved
  service `id/mode` are schema failures
- empty/whitespace-only clause/predicate bare-string import rows are schema failures
- bindings execute once per contract before predicate evaluation
- bindings use additive mapping form (contracts.clauses[].bindings.defaults + contracts.clauses[].bindings.rows[])
- binding shape/alias grammar source:
  `/specs/01_schema/registry/v1/core.yaml and /specs/01_schema/registry/v1/assertions.yaml`
- canonical row key `contract` under `contracts.clauses[].bindings.rows[]` is invalid
- each effective binding row MUST include `id`, `service`, and `import` after defaults merge
- effective row = shallow merge(`contracts.clauses[].bindings.defaults`, row), row values override defaults
- effective `service` MUST reference an existing `adapters[].actions[].id`
- `contracts.clauses[].bindings.rows[].inputs[].from` MUST reference `assets[].id`
- `contracts.clauses[].bindings.rows[].outputs[].to` MUST reference `artifacts[].id`
- binding I/O accepted input forms:
  - `inputs` accepts canonical list[mapping] and compact list[string]
  - `outputs` accepts canonical list[mapping] and compact list[string]
- compact binding I/O canonical normalized forms:
  - input string `"x"` -> `{from: x}`
  - output string `"y"` -> `{to: y}`
- mixed item kinds (string + mapping) in one binding inputs/outputs list are invalid
- empty/whitespace compact binding I/O strings are invalid
- compact binding I/O rows encode `from`/`to` only; `as`/`path` require canonical mapping rows
- binding runtime payload adapter_action MUST use declared asset/artifact ids only (`assets[]` and `artifacts[]`)
- direct external locator keys in `adapters[].actions[].config` are invalid:
  `path`, `url`, `token_url`, `template_path`, `output_path`, `ref`
- every `*_asset_id` in service config MUST resolve to
  `assets[].id`
- every `*_asset_ids[]` entry in service config MUST resolve to
  `assets[].id`
- mixed direct-locator and artifact-id forms for the same semantic field are
  invalid
- `asserts.imports[].from=artifact` and `asserts.checks[].imports[].from=artifact`
  names MUST resolve to suite-declared artifact ids (`artifacts[].id`)
- implicit harness/service target symbol injection is invalid; artifact symbols are
  declaration-and-binding derived only
- synthetic labels may be emitted for reporting when optional docs/docs-owner ids
  are omitted, but these labels are diagnostics-only and must not be accepted as
  schema reference identities
- `contracts.clauses[].bindings.rows[].mode` supports `merge|override` on effective rows:
  - `merge`: explicit imports win collisions
  - `override`: binding-piped symbols overwrite same-name imports

Binding defaults semantics:

- mapping-form `contracts.clauses[].bindings.defaults` applies only to rows in
  `contracts.clauses[].bindings.rows[]`
- row conflicts with defaults resolve in favor of row values
- missing effective `service` or `import` is schema failure
- requiredness model terminology:
  - explicit-required: key must be authored
  - optional: key may be omitted
  - effective-required: key may be inherited but must exist after merge

Clause import canonical semantics:

- compact alias rows are preferred authoring style; canonical rows remain valid
- canonical rows and compact alias rows may coexist in one imports list
- compact artifact alias requires non-empty list of artifact ids
- compact service alias requires `id` and non-empty `names`
- compact bare-string alias is supported and means a service import using
  `contracts.clauses[].bindings.defaults.service`
- unknown keys in compact alias rows are schema failures
- canonical alias grammar source:
  `/specs/01_schema/registry/v1/core.yaml and /specs/01_schema/registry/v1/assertions.yaml`

Binding I/O canonical semantics:

- preferred authoring form for simple binding I/O rows is compact list[string]
- canonical mapping rows remain valid and required when alias/path fields are needed
- compact outputs:
  - `outputs: [body_json, status]` normalizes to canonical rows
    `{to: body_json}`, `{to: status}`
- compact inputs:
  - `inputs: [request_payload]` normalizes to canonical row
    `{from: request_payload}`
- canonical examples for advanced rows:
  - `- to: body_json`
  - `  as: subject`
  - `  path: $.items[0]`

`expect` (conformance metadata):

- `portable` (mapping): shared expectation baseline
- `overrides` (list, optional): runtime-specific overlays with explicit `runner`
- expected keys in `portable`/`overrides[]`:
  - `status`: `pass`, `fail`, or `skip`
  - `category`: `schema` / `assertion` / `runtime` / `null`
  - `message_tokens`: optional list of expected message tokens
- for conformance fixture cases, `expect.portable` with `status` is required

`requires` (metadata):

- `capabilities` (list[string], optional): declared capabilities for the case
- `when_missing` (string, optional): `skip` or `fail` (default `fail`)

## Portable Authoring Profile

For implementation-independent conformance specs:

- Canonical case set lives in `specs/03_conformance/cases/**/*.spec.md`.
- Portable expectations are defined in `expect.portable`.
- Runtime deltas are expressed via `expect.overrides[]`.
- Portable cases SHOULD be deterministic and avoid ambient dependency on:
  - time/date/timezone
  - randomness without explicit seeded input
  - network access
  - undeclared environment variables

Normative contract details:

- `specs/02_contracts/06_conformance.md`
- `specs/02_contracts/07_portable_spec_authoring.md`

## Harness-Profile Fields

### `harness.type: unit.test` with `adapters[].actions[].profile: read.text`

`read.text` asserts against file content.

- External file locators must be declared in `artifacts[]` and referenced
  by id from service config.

Fields:

- `source_asset_id` (string, required): id referencing
  `artifacts[].id` for the text/file source payload.

Assertion targets for `read.text`:

- `text`
- `context_json`: JSON subject profile envelope
- `meta_json`: runtime metadata envelope

Markdown library authoring guidance:

- markdown helper predicates SHOULD target `context_json` when asserting
  structured document properties (headings, links, token ownership/dependencies)
- text-only assertions SHOULD be limited to literal text obligations
- markdown domain helpers accept dual input:
  - raw markdown string
  - markdown profile envelope (`value` + optional `context`)

## Harness Dispatch

Harness dispatch is selected by suite-root `harness` and service execution/binding is selected by suite-root `services[]`. Runtime profile/config data is declared in `harness.profile`/`harness.config` and `adapters[].actions[].profile`/`adapters[].actions[].config`.

Governance assertion contract:

- For governance check profiles, decision obligations MUST be encoded in
  `clauses` blocks.
- ad-hoc service evaluate surfaces are forbidden.
- Extractors may emit candidate violations and subject payloads, but MUST NOT
  be the source of final decision truth.

Assertion targets for `governance.check`:

- `text`: human-readable PASS/FAIL summary output
- `summary_json`: structured summary target; `evaluate` receives summary mapping
  with `passed`, `check_id`, `case_id`, `violation_count`
- `violation_count`: integer violation count target
- `context_json`: optional JSON subject profile envelope
- `meta_json`: runtime metadata envelope

Security model:

- Spec tests are trusted inputs. `exec.command` and hook entrypoints can execute
  project code/commands with runner process privileges.
- Running untrusted spec documents is unsafe and out of scope for v1.
- Implementations MAY pass process environment variables to `exec.command`; keep
  sensitive env values out of runner contexts where possible.
- `data-contracts` is not a sandbox and MUST NOT be presented/documented as one.

For `harness.type: unit.test` with `adapters[].actions[].profile: exec.command`, supported `adapters[].actions[].config` keys include:

- `entrypoint` (string, recommended): CLI entrypoint to call (e.g. `myproj.cli:main`)
- `env` (mapping): env vars to set/unset before running the CLI
- `stdin_isatty` (bool): simulate TTY vs piped stdin
- `stdin_text` (string): text to provide on stdin
- `block_imports` (list[string]): make imports fail with `ModuleNotFoundError`
- `stub_modules` (list[string]): pre-populate `sys.modules` with stubs
- `setup_files` (list[{path, text}]): write files under the runner temp dir
- `hook_before` (string): hook entrypoint invoked before running the CLI
- `hook_after` (string): hook entrypoint invoked after running the CLI
- `hook_kwargs` (mapping): keyword arguments passed through to the hook
- `spec_lang` (mapping): evaluator budgets for `evaluate` leaves
- `orchestration` (mapping): orchestration tool dispatch contract for
  orchestration profiles

For `harness.type: unit.test` with `adapters[].actions[].profile: request.http`, supported `adapters[].actions[].config` keys include:

- `api_http.mode` (string): `deterministic` (default) or `live`
- `api_http.scenario` (mapping, optional):
  - `setup.command` (list[string])
  - `setup.cwd` (virtual-root path, optional)
  - `setup.env` (mapping, optional)
  - `setup.ready_probe` (mapping, optional)
  - `teardown.command` (list[string])
  - `teardown.cwd` (virtual-root path, optional)
  - `teardown.env` (mapping, optional)
  - `fail_fast` (bool, default `true`)
- `api_http.auth.oauth` (mapping):
  - `grant_type`: `client_credentials`
  - `token_asset_id`: artifacts import id for token endpoint locator
  - `client_id_env`: env var name for OAuth client id
  - `client_secret_env`: env var name for OAuth client secret
  - `scope` (optional)
  - `audience` (optional)
  - `auth_style`: `basic` (default) or `body`
  - `token_field`: token field in token response (default `access_token`)
  - `expires_field`: expiry field in token response (default `expires_in`)
  - `refresh_skew_seconds`: cache skew (default `30`)

OAuth and execution rules:

- credentials MUST be env references (`*_env`) only; inline secrets are invalid
- network `http(s)` token/request URLs require `api_http.mode: live`
- deterministic mode forbids network token/request fetches
- context profile metadata MUST redact secret/token values

`request.http` request shape:

- `request` (mapping) for single-request cases, or `requests` (non-empty list) for scenario cases
- request fields:
  - `method`: `GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS`
  - `artifact_id`: artifact id for request locator
  - `headers` (optional mapping)
  - `query` (optional mapping; merged into URL deterministically)
  - `body_text` / `body_json` (mutually exclusive)
  - `cors` (optional mapping):
    - `origin`
    - `request_method` (required when `preflight=true`)
    - `request_headers` (optional list)
    - `preflight` (optional bool, default `false`)

`request.http` common service result symbols (must be explicitly declared/wired before import):

- `cors_json` (normalized CORS projection for final response)
- `steps_json` (ordered step envelopes in scenario mode)

For `harness.type: unit.test` with `adapters[].actions[].profile: generate.docs`, supported `adapters[].actions[].config` keys include:

- `docs_generate.surface_id` (required)
- `docs_generate.mode` (required): `write|check`
- `docs_generate.output_mode` (required): `markers|full_file`
- `docs_generate.template_asset_id` (required): artifacts import id
- `docs_generate.output_artifact_id` (required): artifacts import id
- `docs_generate.marker_surface_id` (required when `output_mode=markers`)
- `docs_generate.data_sources` (required list):
  - `id`
  - `source_type`: `json_file|yaml_file|generated_artifact|command_output`
  - `artifact_id` for file/artifacts source types
  - `command` for `command_output` source type
- `docs_generate.strict` (optional bool, default `true`)

`setup_files[*].path` constraints:

- MUST be relative
- MUST resolve within the runner temp directory (no path escape)

`clauses.config.spec_lang` fields:

- `max_steps` (int, >=1)
- `max_nodes` (int, >=1)
- `max_literal_bytes` (int, >=1)
- `timeout_ms` (int, >=0, `0` disables timeout)
- `includes` (list[string], optional): library include files (library docs only)
- `exports` (list[string], optional): symbol allowlist exposed to this case
- `imports` (list[mapping], optional): case-scoped stdlib imports
  - `from` (string, required): `std.*` namespace prefix
  - `names` (list[string], required): symbols imported from namespace
  - `as` (mapping, optional): alias map `symbol -> local_name`
- `references` (mapping, optional): external reference policy
  - `mode` (string): `deny` (default) or `allow`
  - `providers` (list[string]): allowlisted provider names
  - `rules` (mapping, optional): provider-specific rule payloads for adapters
- `capabilities` (list[string], optional): explicit evaluator capabilities
  (for example `ops.os`).

`clauses.config.spec_lang.includes` format scope:

- library include paths MAY target `.spec.md`, `.spec.yaml`, or `.spec.yml`
  files
- library include paths use virtual-root semantics (`/` means contract root);
  root-relative values normalize to canonical `/...`
- external references use `external://provider/id` and are deny-by-default
  unless capability and harness policy explicitly allow provider access
- producer cases define reusable symbols through root `exports[]` entries using
  `from: assert.function`; function
  bodies are sourced from producer contract-step `asserts` expression mappings
- Canonical export source marker is ``assert.function``.
- default executable case discovery remains Markdown-only (`*.spec.md`) unless
  explicit format opt-in is provided by the runner interface
- executable case types MUST NOT declare `clauses.config.spec_lang.includes`;
  executable symbol loading is chain-first via `harness.chain`

`harness.chain` fields:

- `fail_fast` (bool, optional, default `true`)
- `steps` (list, required when `harness.chain` is present; non-empty)
  - each step:
    - `id` (string, required, unique)
    - `required` (bool, optional, default `true`)
    - `priority` (int, optional, default `1`, minimum `1`)
    - `severity` (int, optional, default `1`, minimum `1`)
    - `purpose` (string, optional, non-empty when provided)
    - `ref` (string, required): `[path][#case_id]`
      - path may be virtual-absolute (`/...`) or relative
      - `#case_id` fragment is optional
      - `#case_id` with no preceding path is valid and resolves in current doc
      - case id fragment must match `[A-Za-z0-9._:-]+` when present
      - YAML authors should quote hash-only refs (for example `ref: "#CASE-1"`)
    - `allow_continue` (bool, optional, default `false`)
- `exports` (list, optional): producer-owned export declarations
  - each entry:
    - `as` (string, required)
    - `from` (string, required; must be `assert.function`)
    - `path` (string, required for `from: assert.function`)
    - `params` (list[string], optional; non-empty when provided)
    - `required` (bool, optional; default `true`)
  - canonical key `from_target` is forbidden
- `imports` (list[mapping], optional)
  - each import:
    - `from` (string, required): source step id
    - `names` (list[string], required): exported names from that step
    - `as` (mapping, optional): alias map `name -> local_name`
  - local imported names and aliases must be unique
  - local imported names and aliases must not shadow reserved names:
    `subject`, `if`, `let`, `fn`, `call`, `var`

Chain reference resolution:

- `#case_id`: resolve one exact case within current `.spec.md` document.
- `path#case_id`: resolve one exact case in referenced document.
- `path`: execute all cases in referenced document in order.
- relative paths resolve from current `.spec.md` document directory.

Chain execution model:

- all executable case types may declare `harness.chain`.
- chain state sharing is explicit via step-level `imports` + `harness.chain.imports`.
- top-level `chain` and type-specific `*.chain` aliases are forbidden.
- scalar `ref` is the only supported reference format; canonical mapping refs are
  invalid.

Chain template interpolation:

- `request.http` request `url`, header values, and `body_text` support
  `{{chain.<step_id>.<export_name>}}` lookups from exported chain state.
- unresolved chain template references are schema/runtime failures.

Documentation generator model:

- docs generation surfaces are declared in
  `specs/01_schema/docs_generator_registry_v1.yaml`.
- generator-owned markdown sections MUST use read-only markers:
  - `<!-- GENERATED:START surface_id -->`
  - `<!-- GENERATED:END surface_id -->`
- CI/governance check mode MUST verify generated docs artifacts are synchronized.

Implementation note:

- `clauses.config.entrypoint` is required for `exec.command` execution.
- Conformance fixtures SHOULD always set explicit entrypoint config.
- Runners MAY provide a safe mode (for example `SPEC_RUNNER_SAFE_MODE=1`) that
  disables hook execution for `exec.command`.
- Runners MAY provide environment allowlisting for subprocess execution (for
  example `SPEC_RUNNER_ENV_ALLOWLIST=K1,K2`).

Assertion targets for `exec.command`:

- `stdout`: text output from command stdout
- `stderr`: text output from command stderr
- `stdout_path`: path printed on first non-empty stdout line
- `stdout_path_text`: UTF-8 text from file at `stdout_path`
- `chain_json`: shared chain state/trace/imports envelope
- `context_json`: JSON subject profile envelope
- `meta_json`: runtime metadata envelope

## Profiles

Currently supported `adapters[].actions[].profile` values include:

- `read.text`
- `fs.readwrite`
- `request.http`
- `exec.command`
- `system.exec`
- `mysql.query`
- `mysql.normalize`
- `generate.docs`

Profile contracts live under:

- `specs/02_contracts/types/`

Domain-specific adapters are expected to publish a matching profile contract doc
before portable conformance usage.

Published extension profile contracts:

- `request.http` (see `specs/02_contracts/types/api_http.md`)

Service model:

- `adapters[].type` is integration-only and MUST be one of:
  `io.fs`, `io.http`, `io.system`, `io.mysql`, `io.docs`
- `adapters[].actions[].profile` is mode-style and validated against the resolved
  type via `service_contract_catalog_v1.yaml`

## Assertion Capability Model (Universal Core)

Universal core assertion model:

- every leaf assertion is a spec-lang mapping AST expression.
- every leaf assertion is represented with operator-keyed mappings.
- universal core operator semantics are evaluate-only at runtime.
- evaluator subjects MUST be JSON values only (`null`, boolean, number, string,
  list, object with string keys).

## Assertion Predicate Shape

`asserts` is a mapping with:

- `imports` (optional list)
- `checks` (required list)

Each `checks[]` entry requires:

- `id` (string, unique per case)
- `assert` (non-empty expression mapping or list)
- `imports` (optional list)
- `purpose` (optional string)
- `required` (optional bool, default `true`)
- `priority` (optional int, default `1`, must be `>=1`)
- `severity` (optional int, default `1`, must be `>=1`)

Import binding shape:

- `imports` is a list that accepts canonical mapping items and compact alias items
- canonical item requires `from` and `names`, with optional `as`
- compact grouped aliases are allowed per row:
  - artifact alias: `{artifact: [id_a, id_b]}`
  - service alias: `{service: {id: svc.x, names: [...], as?: {...}}}`
  - service short alias: `"pipe_identity"` (normalized using
    `contracts.clauses[].bindings.defaults.service`)
- compact aliases normalize to canonical rows before validation/execution
- canonical assertion imports may use `from: asset`, `from: artifact`, or `from: service`
- short string aliases are always interpreted as `from: service` imports
- when `from: asset`, `names` must be a non-empty list of suite-declared
  artifact ids (and be explicitly wired when runtime-produced)
- for short string aliases, `contracts.clauses[].bindings.defaults.service` must exist
  and resolve to `adapters[].actions[].id`
- `as` is optional mapping `source_name -> local_name`

Import merge behavior:

- effective check imports = `asserts.imports` merged with
  `asserts.checks[].imports`
- check imports override assertion-level imports on key collision
- binding-piped symbols are then merged into effective predicate context
  according to `contracts.clauses[].bindings.rows[].mode`:
  - `merge`: existing explicit import symbols are preserved
  - `override`: binding symbols replace same-name explicit imports

Symbol resolution:

- `{var: subject}` is valid only when `subject` is explicitly imported

Supported operators:

- universal core operator: spec-lang v1 operator-keyed mappings at each leaf

Core executable-surface rule:

- `specs/03_conformance/cases/**/*.spec.md` assertion trees MUST use
  direct spec-lang expression leaves.
- `specs/04_governance/cases/**/*.spec.md` assertion trees MUST use
  direct spec-lang expression leaves.

Operator constraints:

- all operator values MUST be lists
- each assertion leaf MUST be an expression node using an operator-keyed mapping
- subject reference node: `{var: subject}` resolves via explicit imports
- bare scalar `subject` is a literal string (not a reference)
- spec-lang semantics and budget model are defined in
  `specs/02_contracts/03b_spec_lang_v1.md`
- spec-lang v1 includes deep-equality set algebra (`union`, `intersection`,
  `difference`, `symmetric_difference`, `is_subset`, `is_superset`,
  `set_equals`) and collection transforms (`map`, `filter`, `reduce`, etc.)
  with automatic builtin currying semantics
- spec-lang ramda-style utility surface includes strict numeric math
  (`mul`, `div`, `mod`, `pow`, `abs`, `negate`, `inc`, `dec`, `clamp`,
  `round`, `floor`, `ceil`), comparison/logical helpers (`compare`, `between`,
  `xor`), list utilities (`slice`, `reverse`, `zip`, `zip_with`, `range`,
  `repeat`), object helpers (`keys`, `values`, `actions`, `merge`, `assoc`,
  `dissoc`, `pick`, `omit`), and compositional predicates/combinators
  (`prop_eq`, `where`, `compose`, `pipe`, `identity`, `always`, `replace`,
  `pad_left`, `pad_right`) plus explicit JSON-type predicates (`is_null`,
  `is_bool`/`is_boolean`, `is_number`, `is_string`,
  `is_list`/`is_array`, `is_dict`/`is_object`)
- spec-lang shared library loading rules are defined in
  `specs/02_contracts/14_spec_lang_libraries.md`
- runtime pass/fail decisions MUST execute through compiled spec-lang
  expressions
- orchestration effect symbol names use deep-dot `ops.*` hierarchy:
  `ops.<segment>(.<segment>)+` (for example `ops.fs.file.read`,
  `ops.proc.command.exec`)
- pure spec-lang utility symbols may also use `ops.*` namespaces
  (for example `ops.fs.path.normalize`, `ops.fs.file.exists`) and MUST remain
  deterministic with no evaluator side effects
- pure JSON helpers under `ops.fs.json.*` are allowed for parse/path lookup
  (`parse`, `get`, `get_or`, `has_path`) and remain evaluator-pure
- pure glob helpers under `ops.fs.glob.*` are allowed for deterministic
  pattern matching/filtering (`match`, `filter`, `any`, `all`)
- underscore shorthand ops symbols are invalid
- path fields in scoped harness/type config use virtual-root canonical `/...`
  form; `..` contract-root escapes are invalid
- regex portability guidance for spec-lang expressions is defined in
  `specs/02_contracts/03a_regex_portability_v1.md`

Step metadata constraints:

- `asserts.checks[].required` is optional and defaults to `true`
- `asserts.checks[].priority` is optional integer metadata (`>=1`, default `1`)
- `asserts.checks[].severity` is optional integer metadata (`>=1`, default `1`)
- `asserts.checks[].purpose` is optional human-readable text
- optional checks (`required: false`) are non-blocking for overall case verdict
- prohibition intent is expressed directly with negation operators
  (for example `std.logic.not`)

Canonical negation form:

```yaml
asserts:
  imports:
  - from: asset
    names: [text]
    as:
      text: subject
  checks:
  - id: assert_no_error
    required: true
    assert:
      std.logic.not:
      - std.string.contains:
        - {var: subject}
        - 'ERROR:'
```

Author in canonical form:

- use explicit assertion expressions; do not use step classes
- use `required: false` for non-blocking steps
- use `priority` / `severity` as metadata-only ranking hints
- use direct operator mappings in `assert` (no `evaluate` wrapper)
- put every operator value in a list

Example with check-level import override:

```yaml
asserts:
  imports:
  - from: asset
    names: [summary_json]
    as:
      summary_json: subject
  checks:
  - id: assert_passed
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: subject}
        - passed
      - true
  - id: assert_violation_count
    imports:
    - from: asset
      names: [violation_count]
      as:
        violation_count: subject
    assert:
      std.logic.eq:
      - {var: subject}
      - 0
```

`when` lifecycle hooks:

- optional `when` mapping on executable cases
- allowed keys:
  - `required`
  - `optional`
  - `fail`
  - `complete`
- each hook key, when present, must be a non-empty list of mapping-AST expressions
- hook expressions evaluate with existing case spec-lang limits/imports/symbols/capabilities
- hook failures are runtime-fatal

Lifecycle order:

- `required` hook runs after successful required-step evaluation
- `optional` hook runs after successful optional-step evaluation
- `fail` runs once on first blocking step or hook failure
- `complete` runs only after all steps and hooks pass

Job orchestration note:

- `ops.job.dispatch` remains a spec-lang capability surface.
- job/export orchestration semantics are not modeled as service types in v1.

<!-- BEGIN GENERATED: SCHEMA_REGISTRY_V2 -->

## Generated Registry Snapshot

This section is generated from `specs/01_schema/registry/v1/*.yaml`.

- profile_count: 4
- top_level_fields: 221
- service_catalog: `/specs/01_schema/service_contract_catalog_v1.yaml`

### Top-Level Keys

| key | type | required | since |
|---|---|---|---|
| `spec_version` | `int` | `true` | `v1` |
| `schema_ref` | `string` | `true` | `v1` |
| `harness` | `mapping` | `true` | `v1` |
| `harness.type` | `string` | `true` | `v1` |
| `harness.profile` | `string` | `true` | `v1` |
| `harness.config` | `mapping` | `false` | `v1` |
| `harness.docs` | `list` | `false` | `v1` |
| `harness.docs[].id` | `string` | `false` | `v1` |
| `harness.docs[].summary` | `string` | `true` | `v1` |
| `harness.docs[].audience` | `string` | `true` | `v1` |
| `harness.docs[].status` | `string` | `true` | `v1` |
| `harness.docs[].description` | `string` | `false` | `v1` |
| `harness.docs[].type` | `string` | `false` | `v1` |
| `harness.docs[].since` | `string` | `false` | `v1` |
| `harness.docs[].updated_at` | `string` | `false` | `v1` |
| `harness.docs[].tags` | `list` | `false` | `v1` |
| `harness.docs[].owners` | `list` | `false` | `v1` |
| `harness.docs[].owners[].id` | `string` | `false` | `v1` |
| `harness.docs[].owners[].role` | `string` | `true` | `v1` |
| `harness.docs[].links` | `list` | `false` | `v1` |
| `harness.docs[].links[].rel` | `string` | `true` | `v1` |
| `harness.docs[].links[].ref` | `string` | `true` | `v1` |
| `harness.docs[].links[].title` | `string` | `false` | `v1` |
| `harness.docs[].examples` | `list` | `false` | `v1` |
| `harness.docs[].examples[].title` | `string` | `true` | `v1` |
| `harness.docs[].examples[].ref` | `string` | `true` | `v1` |
| `services` | `mapping` | `false` | `v1` |
| `adapters[].type` | `string` | `true` | `v1` |
| `adapters[].type` | `string` | `false` | `v1` |
| `adapters[].actions[].direction` | `string` | `false` | `v1` |
| `adapters[].actions[].profile` | `string` | `false` | `v1` |
| `adapters[].actions[].config` | `mapping` | `false` | `v1` |
| `adapters[].actions[].imports` | `list` | `false` | `v1` |
| `adapters[].actions[].imports[].names` | `list` | `true` | `v1` |
| `adapters[].actions[].imports[].as` | `mapping` | `false` | `v1` |
| `services[].docs` | `list` | `false` | `v1` |
| `services[].docs[].id` | `string` | `false` | `v1` |
| `services[].docs[].summary` | `string` | `true` | `v1` |
| `services[].docs[].audience` | `string` | `true` | `v1` |
| `services[].docs[].status` | `string` | `true` | `v1` |
| `services[].docs[].description` | `string` | `false` | `v1` |
| `services[].docs[].type` | `string` | `false` | `v1` |
| `services[].docs[].since` | `string` | `false` | `v1` |
| `services[].docs[].updated_at` | `string` | `false` | `v1` |
| `services[].docs[].tags` | `list` | `false` | `v1` |
| `services[].docs[].owners` | `list` | `false` | `v1` |
| `services[].docs[].owners[].id` | `string` | `false` | `v1` |
| `services[].docs[].owners[].role` | `string` | `true` | `v1` |
| `services[].docs[].links` | `list` | `false` | `v1` |
| `services[].docs[].links[].rel` | `string` | `true` | `v1` |
| `services[].docs[].links[].ref` | `string` | `true` | `v1` |
| `services[].docs[].links[].title` | `string` | `false` | `v1` |
| `services[].docs[].examples` | `list` | `false` | `v1` |
| `services[].docs[].examples[].title` | `string` | `true` | `v1` |
| `services[].docs[].examples[].ref` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings` | `any` | `false` | `v1` |
| `contracts.clauses[].bindings.defaults` | `mapping` | `false` | `v1` |
| `contracts.clauses[].bindings.defaults.service` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.defaults.import` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.defaults.mode` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.defaults.predicates` | `list` | `false` | `v1` |
| `contracts.clauses[].bindings.rows` | `list` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].id` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings.rows[].service` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].import` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].inputs` | `list` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].inputs[].from` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings.rows[].inputs[].as` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings.rows[].outputs` | `list` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].to` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].as` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].path` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].predicates` | `list` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].mode` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].id` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings.rows[].service` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].import` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].inputs` | `list` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].inputs[].from` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings.rows[].inputs[].as` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings.rows[].outputs` | `list` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].to` | `string` | `true` | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].as` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].path` | `string` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].predicates` | `list` | `false` | `v1` |
| `contracts.clauses[].bindings.rows[].mode` | `string` | `false` | `v1` |
| `artifacts` | `mapping` | `false` | `v1` |
| `artifacts` | `list` | `false` | `v1` |
| `artifacts[].id` | `string` | `true` | `v1` |
| `artifacts[].ref` | `string` | `true` | `v1` |
| `artifacts[].type` | `string` | `false` | `v1` |
| `artifacts[].inputs` | `mapping` | `false` | `v1` |
| `artifacts[].options` | `mapping` | `false` | `v1` |
| `artifacts[].docs` | `list` | `false` | `v1` |
| `artifacts[].docs[].id` | `string` | `false` | `v1` |
| `artifacts[].docs[].summary` | `string` | `true` | `v1` |
| `artifacts[].docs[].audience` | `string` | `true` | `v1` |
| `artifacts[].docs[].status` | `string` | `true` | `v1` |
| `artifacts[].docs[].description` | `string` | `false` | `v1` |
| `artifacts[].docs[].type` | `string` | `false` | `v1` |
| `artifacts[].docs[].since` | `string` | `false` | `v1` |
| `artifacts[].docs[].updated_at` | `string` | `false` | `v1` |
| `artifacts[].docs[].tags` | `list` | `false` | `v1` |
| `artifacts[].docs[].owners` | `list` | `false` | `v1` |
| `artifacts[].docs[].owners[].id` | `string` | `false` | `v1` |
| `artifacts[].docs[].owners[].role` | `string` | `true` | `v1` |
| `artifacts[].docs[].links` | `list` | `false` | `v1` |
| `artifacts[].docs[].links[].rel` | `string` | `true` | `v1` |
| `artifacts[].docs[].links[].ref` | `string` | `true` | `v1` |
| `artifacts[].docs[].links[].title` | `string` | `false` | `v1` |
| `artifacts[].docs[].examples` | `list` | `false` | `v1` |
| `artifacts[].docs[].examples[].title` | `string` | `true` | `v1` |
| `artifacts[].docs[].examples[].ref` | `string` | `true` | `v1` |
| `artifacts` | `list` | `false` | `v1` |
| `artifacts[].id` | `string` | `true` | `v1` |
| `artifacts[].ref` | `string` | `true` | `v1` |
| `artifacts[].type` | `string` | `false` | `v1` |
| `artifacts[].options` | `mapping` | `false` | `v1` |
| `artifacts[].docs` | `list` | `false` | `v1` |
| `artifacts[].docs[].id` | `string` | `false` | `v1` |
| `artifacts[].docs[].summary` | `string` | `true` | `v1` |
| `artifacts[].docs[].audience` | `string` | `true` | `v1` |
| `artifacts[].docs[].status` | `string` | `true` | `v1` |
| `artifacts[].docs[].description` | `string` | `false` | `v1` |
| `artifacts[].docs[].type` | `string` | `false` | `v1` |
| `artifacts[].docs[].since` | `string` | `false` | `v1` |
| `artifacts[].docs[].updated_at` | `string` | `false` | `v1` |
| `artifacts[].docs[].tags` | `list` | `false` | `v1` |
| `artifacts[].docs[].owners` | `list` | `false` | `v1` |
| `artifacts[].docs[].owners[].id` | `string` | `false` | `v1` |
| `artifacts[].docs[].owners[].role` | `string` | `true` | `v1` |
| `artifacts[].docs[].links` | `list` | `false` | `v1` |
| `artifacts[].docs[].links[].rel` | `string` | `true` | `v1` |
| `artifacts[].docs[].links[].ref` | `string` | `true` | `v1` |
| `artifacts[].docs[].links[].title` | `string` | `false` | `v1` |
| `artifacts[].docs[].examples` | `list` | `false` | `v1` |
| `artifacts[].docs[].examples[].title` | `string` | `true` | `v1` |
| `artifacts[].docs[].examples[].ref` | `string` | `true` | `v1` |
| `exports` | `list` | `false` | `v1` |
| `exports[].as` | `string` | `true` | `v1` |
| `exports[].from` | `string` | `true` | `v1` |
| `exports[].path` | `string` | `true` | `v1` |
| `exports[].params` | `list` | `false` | `v1` |
| `exports[].required` | `bool` | `false` | `v1` |
| `exports[].docs` | `list` | `false` | `v1` |
| `exports[].docs[].id` | `string` | `false` | `v1` |
| `exports[].docs[].summary` | `string` | `true` | `v1` |
| `exports[].docs[].audience` | `string` | `true` | `v1` |
| `exports[].docs[].status` | `string` | `true` | `v1` |
| `exports[].docs[].description` | `string` | `false` | `v1` |
| `exports[].docs[].type` | `string` | `false` | `v1` |
| `exports[].docs[].since` | `string` | `false` | `v1` |
| `exports[].docs[].updated_at` | `string` | `false` | `v1` |
| `exports[].docs[].tags` | `list` | `false` | `v1` |
| `exports[].docs[].owners` | `list` | `false` | `v1` |
| `exports[].docs[].owners[].id` | `string` | `false` | `v1` |
| `exports[].docs[].owners[].role` | `string` | `true` | `v1` |
| `exports[].docs[].links` | `list` | `false` | `v1` |
| `exports[].docs[].links[].rel` | `string` | `true` | `v1` |
| `exports[].docs[].links[].ref` | `string` | `true` | `v1` |
| `exports[].docs[].links[].title` | `string` | `false` | `v1` |
| `exports[].docs[].examples` | `list` | `false` | `v1` |
| `exports[].docs[].examples[].title` | `string` | `true` | `v1` |
| `exports[].docs[].examples[].ref` | `string` | `true` | `v1` |
| `contracts` | `list` | `true` | `v1` |
| `contracts.clauses[].id` | `string` | `true` | `v1` |
| `title` | `string` | `false` | `v1` |
| `purpose` | `string` | `false` | `v1` |
| `docs` | `list` | `false` | `v1` |
| `docs[].id` | `string` | `false` | `v1` |
| `docs[].summary` | `string` | `true` | `v1` |
| `docs[].audience` | `string` | `true` | `v1` |
| `docs[].status` | `string` | `true` | `v1` |
| `docs[].description` | `string` | `false` | `v1` |
| `docs[].type` | `string` | `false` | `v1` |
| `docs[].since` | `string` | `false` | `v1` |
| `docs[].updated_at` | `string` | `false` | `v1` |
| `docs[].tags` | `list` | `false` | `v1` |
| `docs[].owners` | `list` | `false` | `v1` |
| `docs[].owners[].id` | `string` | `false` | `v1` |
| `docs[].owners[].role` | `string` | `true` | `v1` |
| `docs[].links` | `list` | `false` | `v1` |
| `docs[].links[].rel` | `string` | `true` | `v1` |
| `docs[].links[].ref` | `string` | `true` | `v1` |
| `docs[].links[].title` | `string` | `false` | `v1` |
| `docs[].examples` | `list` | `false` | `v1` |
| `docs[].examples[].title` | `string` | `true` | `v1` |
| `docs[].examples[].ref` | `string` | `true` | `v1` |
| `domain` | `string` | `false` | `v1` |
| `contracts.clauses[].title` | `string` | `false` | `v1` |
| `contracts.clauses[].purpose` | `string` | `false` | `v1` |
| `contracts.clauses[].domain` | `string` | `false` | `v1` |
| `contracts.clauses[].docs` | `list` | `false` | `v1` |
| `contracts.clauses[].docs[].id` | `string` | `false` | `v1` |
| `contracts.clauses[].docs[].summary` | `string` | `true` | `v1` |
| `contracts.clauses[].docs[].audience` | `string` | `true` | `v1` |
| `contracts.clauses[].docs[].status` | `string` | `true` | `v1` |
| `contracts.clauses[].docs[].description` | `string` | `false` | `v1` |
| `contracts.clauses[].docs[].type` | `string` | `false` | `v1` |
| `contracts.clauses[].docs[].since` | `string` | `false` | `v1` |
| `contracts.clauses[].docs[].updated_at` | `string` | `false` | `v1` |
| `contracts.clauses[].docs[].tags` | `list` | `false` | `v1` |
| `contracts.clauses[].docs[].owners` | `list` | `false` | `v1` |
| `contracts.clauses[].docs[].owners[].id` | `string` | `false` | `v1` |
| `contracts.clauses[].docs[].owners[].role` | `string` | `true` | `v1` |
| `contracts.clauses[].docs[].links` | `list` | `false` | `v1` |
| `contracts.clauses[].docs[].links[].rel` | `string` | `true` | `v1` |
| `contracts.clauses[].docs[].links[].ref` | `string` | `true` | `v1` |
| `contracts.clauses[].docs[].links[].title` | `string` | `false` | `v1` |
| `contracts.clauses[].docs[].examples` | `list` | `false` | `v1` |
| `contracts.clauses[].docs[].examples[].title` | `string` | `true` | `v1` |
| `contracts.clauses[].docs[].examples[].ref` | `string` | `true` | `v1` |
| `contracts.clauses[].when` | `mapping` | `false` | `v1` |
| `contracts.clauses[].when.required` | `list` | `false` | `v1` |
| `contracts.clauses[].when.optional` | `list` | `false` | `v1` |
| `contracts.clauses[].when.fail` | `list` | `false` | `v1` |
| `contracts.clauses[].when.complete` | `list` | `false` | `v1` |
| `contracts.clauses[].asserts` | `mapping` | `true` | `v1` |
| `contracts.clauses[].expect` | `mapping` | `false` | `v1` |
| `contracts.clauses[].expect.portable` | `mapping` | `false` | `v1` |
| `contracts.clauses[].expect.portable.status` | `string` | `false` | `v1` |
| `contracts.clauses[].expect.portable.category` | `string` | `false` | `v1` |
| `contracts.clauses[].expect.portable.message_tokens` | `list` | `false` | `v1` |
| `contracts.clauses[].expect.overrides` | `list` | `false` | `v1` |
| `contracts.clauses[].expect.overrides[].runner` | `string` | `true` | `v1` |
| `contracts.clauses[].expect.overrides[].status` | `string` | `false` | `v1` |
| `contracts.clauses[].expect.overrides[].category` | `string` | `false` | `v1` |
| `contracts.clauses[].expect.overrides[].message_tokens` | `list` | `false` | `v1` |
| `contracts.clauses[].requires` | `mapping` | `false` | `v1` |

### Runtime Surfaces

| surface | required keys | catalog |
|---|---|---|
| `harness` | `harness.type`, `harness.profile` | n/a |
| `services[]` | `adapters[].type` (required when `services` is present, or when `contracts.clauses[].bindings.rows[]` / `from: service` imports are used) | `/specs/01_schema/service_contract_catalog_v1.yaml` |
| `contracts.clauses[].bindings.rows[]` | `contracts.clauses[].bindings.rows[].id`, `contracts.clauses[].bindings.rows[].import` | `/specs/01_schema/service_contract_catalog_v1.yaml` |

<!-- END GENERATED: SCHEMA_REGISTRY_V2 -->
<!-- GENERATED:START spec_schema_field_catalog -->

## Generated Spec Schema Field Catalog

- top_level_field_count: 221
- harness_surface: suite-root `harness`
- service_catalog: `/specs/01_schema/service_contract_catalog_v1.yaml`

### Top-Level Fields

| key | type | required | since |
|---|---|---|---|
| `spec_version` | `int` | true | `v1` |
| `schema_ref` | `string` | true | `v1` |
| `harness` | `mapping` | true | `v1` |
| `harness.type` | `string` | true | `v1` |
| `harness.profile` | `string` | true | `v1` |
| `harness.config` | `mapping` | false | `v1` |
| `harness.docs` | `list` | false | `v1` |
| `harness.docs[].id` | `string` | false | `v1` |
| `harness.docs[].summary` | `string` | true | `v1` |
| `harness.docs[].audience` | `string` | true | `v1` |
| `harness.docs[].status` | `string` | true | `v1` |
| `harness.docs[].description` | `string` | false | `v1` |
| `harness.docs[].type` | `string` | false | `v1` |
| `harness.docs[].since` | `string` | false | `v1` |
| `harness.docs[].updated_at` | `string` | false | `v1` |
| `harness.docs[].tags` | `list` | false | `v1` |
| `harness.docs[].owners` | `list` | false | `v1` |
| `harness.docs[].owners[].id` | `string` | false | `v1` |
| `harness.docs[].owners[].role` | `string` | true | `v1` |
| `harness.docs[].links` | `list` | false | `v1` |
| `harness.docs[].links[].rel` | `string` | true | `v1` |
| `harness.docs[].links[].ref` | `string` | true | `v1` |
| `harness.docs[].links[].title` | `string` | false | `v1` |
| `harness.docs[].examples` | `list` | false | `v1` |
| `harness.docs[].examples[].title` | `string` | true | `v1` |
| `harness.docs[].examples[].ref` | `string` | true | `v1` |
| `services` | `mapping` | false | `v1` |
| `adapters[].type` | `string` | true | `v1` |
| `adapters[].type` | `string` | false | `v1` |
| `adapters[].actions[].direction` | `string` | false | `v1` |
| `adapters[].actions[].profile` | `string` | false | `v1` |
| `adapters[].actions[].config` | `mapping` | false | `v1` |
| `adapters[].actions[].imports` | `list` | false | `v1` |
| `adapters[].actions[].imports[].names` | `list` | true | `v1` |
| `adapters[].actions[].imports[].as` | `mapping` | false | `v1` |
| `services[].docs` | `list` | false | `v1` |
| `services[].docs[].id` | `string` | false | `v1` |
| `services[].docs[].summary` | `string` | true | `v1` |
| `services[].docs[].audience` | `string` | true | `v1` |
| `services[].docs[].status` | `string` | true | `v1` |
| `services[].docs[].description` | `string` | false | `v1` |
| `services[].docs[].type` | `string` | false | `v1` |
| `services[].docs[].since` | `string` | false | `v1` |
| `services[].docs[].updated_at` | `string` | false | `v1` |
| `services[].docs[].tags` | `list` | false | `v1` |
| `services[].docs[].owners` | `list` | false | `v1` |
| `services[].docs[].owners[].id` | `string` | false | `v1` |
| `services[].docs[].owners[].role` | `string` | true | `v1` |
| `services[].docs[].links` | `list` | false | `v1` |
| `services[].docs[].links[].rel` | `string` | true | `v1` |
| `services[].docs[].links[].ref` | `string` | true | `v1` |
| `services[].docs[].links[].title` | `string` | false | `v1` |
| `services[].docs[].examples` | `list` | false | `v1` |
| `services[].docs[].examples[].title` | `string` | true | `v1` |
| `services[].docs[].examples[].ref` | `string` | true | `v1` |
| `contracts.clauses[].bindings` | `any` | false | `v1` |
| `contracts.clauses[].bindings.defaults` | `mapping` | false | `v1` |
| `contracts.clauses[].bindings.defaults.service` | `string` | false | `v1` |
| `contracts.clauses[].bindings.defaults.import` | `string` | false | `v1` |
| `contracts.clauses[].bindings.defaults.mode` | `string` | false | `v1` |
| `contracts.clauses[].bindings.defaults.predicates` | `list` | false | `v1` |
| `contracts.clauses[].bindings.rows` | `list` | false | `v1` |
| `contracts.clauses[].bindings.rows[].id` | `string` | true | `v1` |
| `contracts.clauses[].bindings.rows[].service` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].import` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].inputs` | `list` | false | `v1` |
| `contracts.clauses[].bindings.rows[].inputs[].from` | `string` | true | `v1` |
| `contracts.clauses[].bindings.rows[].inputs[].as` | `string` | true | `v1` |
| `contracts.clauses[].bindings.rows[].outputs` | `list` | false | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].to` | `string` | true | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].as` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].path` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].predicates` | `list` | false | `v1` |
| `contracts.clauses[].bindings.rows[].mode` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].id` | `string` | true | `v1` |
| `contracts.clauses[].bindings.rows[].service` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].import` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].inputs` | `list` | false | `v1` |
| `contracts.clauses[].bindings.rows[].inputs[].from` | `string` | true | `v1` |
| `contracts.clauses[].bindings.rows[].inputs[].as` | `string` | true | `v1` |
| `contracts.clauses[].bindings.rows[].outputs` | `list` | false | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].to` | `string` | true | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].as` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].outputs[].path` | `string` | false | `v1` |
| `contracts.clauses[].bindings.rows[].predicates` | `list` | false | `v1` |
| `contracts.clauses[].bindings.rows[].mode` | `string` | false | `v1` |
| `artifacts` | `mapping` | false | `v1` |
| `artifacts` | `list` | false | `v1` |
| `artifacts[].id` | `string` | true | `v1` |
| `artifacts[].ref` | `string` | true | `v1` |
| `artifacts[].type` | `string` | false | `v1` |
| `artifacts[].inputs` | `mapping` | false | `v1` |
| `artifacts[].options` | `mapping` | false | `v1` |
| `artifacts[].docs` | `list` | false | `v1` |
| `artifacts[].docs[].id` | `string` | false | `v1` |
| `artifacts[].docs[].summary` | `string` | true | `v1` |
| `artifacts[].docs[].audience` | `string` | true | `v1` |
| `artifacts[].docs[].status` | `string` | true | `v1` |
| `artifacts[].docs[].description` | `string` | false | `v1` |
| `artifacts[].docs[].type` | `string` | false | `v1` |
| `artifacts[].docs[].since` | `string` | false | `v1` |
| `artifacts[].docs[].updated_at` | `string` | false | `v1` |
| `artifacts[].docs[].tags` | `list` | false | `v1` |
| `artifacts[].docs[].owners` | `list` | false | `v1` |
| `artifacts[].docs[].owners[].id` | `string` | false | `v1` |
| `artifacts[].docs[].owners[].role` | `string` | true | `v1` |
| `artifacts[].docs[].links` | `list` | false | `v1` |
| `artifacts[].docs[].links[].rel` | `string` | true | `v1` |
| `artifacts[].docs[].links[].ref` | `string` | true | `v1` |
| `artifacts[].docs[].links[].title` | `string` | false | `v1` |
| `artifacts[].docs[].examples` | `list` | false | `v1` |
| `artifacts[].docs[].examples[].title` | `string` | true | `v1` |
| `artifacts[].docs[].examples[].ref` | `string` | true | `v1` |
| `artifacts` | `list` | false | `v1` |
| `artifacts[].id` | `string` | true | `v1` |
| `artifacts[].ref` | `string` | true | `v1` |
| `artifacts[].type` | `string` | false | `v1` |
| `artifacts[].options` | `mapping` | false | `v1` |
| `artifacts[].docs` | `list` | false | `v1` |
| `artifacts[].docs[].id` | `string` | false | `v1` |
| `artifacts[].docs[].summary` | `string` | true | `v1` |
| `artifacts[].docs[].audience` | `string` | true | `v1` |
| `artifacts[].docs[].status` | `string` | true | `v1` |
| `artifacts[].docs[].description` | `string` | false | `v1` |
| `artifacts[].docs[].type` | `string` | false | `v1` |
| `artifacts[].docs[].since` | `string` | false | `v1` |
| `artifacts[].docs[].updated_at` | `string` | false | `v1` |
| `artifacts[].docs[].tags` | `list` | false | `v1` |
| `artifacts[].docs[].owners` | `list` | false | `v1` |
| `artifacts[].docs[].owners[].id` | `string` | false | `v1` |
| `artifacts[].docs[].owners[].role` | `string` | true | `v1` |
| `artifacts[].docs[].links` | `list` | false | `v1` |
| `artifacts[].docs[].links[].rel` | `string` | true | `v1` |
| `artifacts[].docs[].links[].ref` | `string` | true | `v1` |
| `artifacts[].docs[].links[].title` | `string` | false | `v1` |
| `artifacts[].docs[].examples` | `list` | false | `v1` |
| `artifacts[].docs[].examples[].title` | `string` | true | `v1` |
| `artifacts[].docs[].examples[].ref` | `string` | true | `v1` |
| `exports` | `list` | false | `v1` |
| `exports[].as` | `string` | true | `v1` |
| `exports[].from` | `string` | true | `v1` |
| `exports[].path` | `string` | true | `v1` |
| `exports[].params` | `list` | false | `v1` |
| `exports[].required` | `bool` | false | `v1` |
| `exports[].docs` | `list` | false | `v1` |
| `exports[].docs[].id` | `string` | false | `v1` |
| `exports[].docs[].summary` | `string` | true | `v1` |
| `exports[].docs[].audience` | `string` | true | `v1` |
| `exports[].docs[].status` | `string` | true | `v1` |
| `exports[].docs[].description` | `string` | false | `v1` |
| `exports[].docs[].type` | `string` | false | `v1` |
| `exports[].docs[].since` | `string` | false | `v1` |
| `exports[].docs[].updated_at` | `string` | false | `v1` |
| `exports[].docs[].tags` | `list` | false | `v1` |
| `exports[].docs[].owners` | `list` | false | `v1` |
| `exports[].docs[].owners[].id` | `string` | false | `v1` |
| `exports[].docs[].owners[].role` | `string` | true | `v1` |
| `exports[].docs[].links` | `list` | false | `v1` |
| `exports[].docs[].links[].rel` | `string` | true | `v1` |
| `exports[].docs[].links[].ref` | `string` | true | `v1` |
| `exports[].docs[].links[].title` | `string` | false | `v1` |
| `exports[].docs[].examples` | `list` | false | `v1` |
| `exports[].docs[].examples[].title` | `string` | true | `v1` |
| `exports[].docs[].examples[].ref` | `string` | true | `v1` |
| `contracts` | `list` | true | `v1` |
| `contracts.clauses[].id` | `string` | true | `v1` |
| `title` | `string` | false | `v1` |
| `purpose` | `string` | false | `v1` |
| `docs` | `list` | false | `v1` |
| `docs[].id` | `string` | false | `v1` |
| `docs[].summary` | `string` | true | `v1` |
| `docs[].audience` | `string` | true | `v1` |
| `docs[].status` | `string` | true | `v1` |
| `docs[].description` | `string` | false | `v1` |
| `docs[].type` | `string` | false | `v1` |
| `docs[].since` | `string` | false | `v1` |
| `docs[].updated_at` | `string` | false | `v1` |
| `docs[].tags` | `list` | false | `v1` |
| `docs[].owners` | `list` | false | `v1` |
| `docs[].owners[].id` | `string` | false | `v1` |
| `docs[].owners[].role` | `string` | true | `v1` |
| `docs[].links` | `list` | false | `v1` |
| `docs[].links[].rel` | `string` | true | `v1` |
| `docs[].links[].ref` | `string` | true | `v1` |
| `docs[].links[].title` | `string` | false | `v1` |
| `docs[].examples` | `list` | false | `v1` |
| `docs[].examples[].title` | `string` | true | `v1` |
| `docs[].examples[].ref` | `string` | true | `v1` |
| `domain` | `string` | false | `v1` |
| `contracts.clauses[].title` | `string` | false | `v1` |
| `contracts.clauses[].purpose` | `string` | false | `v1` |
| `contracts.clauses[].domain` | `string` | false | `v1` |
| `contracts.clauses[].docs` | `list` | false | `v1` |
| `contracts.clauses[].docs[].id` | `string` | false | `v1` |
| `contracts.clauses[].docs[].summary` | `string` | true | `v1` |
| `contracts.clauses[].docs[].audience` | `string` | true | `v1` |
| `contracts.clauses[].docs[].status` | `string` | true | `v1` |
| `contracts.clauses[].docs[].description` | `string` | false | `v1` |
| `contracts.clauses[].docs[].type` | `string` | false | `v1` |
| `contracts.clauses[].docs[].since` | `string` | false | `v1` |
| `contracts.clauses[].docs[].updated_at` | `string` | false | `v1` |
| `contracts.clauses[].docs[].tags` | `list` | false | `v1` |
| `contracts.clauses[].docs[].owners` | `list` | false | `v1` |
| `contracts.clauses[].docs[].owners[].id` | `string` | false | `v1` |
| `contracts.clauses[].docs[].owners[].role` | `string` | true | `v1` |
| `contracts.clauses[].docs[].links` | `list` | false | `v1` |
| `contracts.clauses[].docs[].links[].rel` | `string` | true | `v1` |
| `contracts.clauses[].docs[].links[].ref` | `string` | true | `v1` |
| `contracts.clauses[].docs[].links[].title` | `string` | false | `v1` |
| `contracts.clauses[].docs[].examples` | `list` | false | `v1` |
| `contracts.clauses[].docs[].examples[].title` | `string` | true | `v1` |
| `contracts.clauses[].docs[].examples[].ref` | `string` | true | `v1` |
| `contracts.clauses[].when` | `mapping` | false | `v1` |
| `contracts.clauses[].when.required` | `list` | false | `v1` |
| `contracts.clauses[].when.optional` | `list` | false | `v1` |
| `contracts.clauses[].when.fail` | `list` | false | `v1` |
| `contracts.clauses[].when.complete` | `list` | false | `v1` |
| `contracts.clauses[].asserts` | `mapping` | true | `v1` |
| `contracts.clauses[].expect` | `mapping` | false | `v1` |
| `contracts.clauses[].expect.portable` | `mapping` | false | `v1` |
| `contracts.clauses[].expect.portable.status` | `string` | false | `v1` |
| `contracts.clauses[].expect.portable.category` | `string` | false | `v1` |
| `contracts.clauses[].expect.portable.message_tokens` | `list` | false | `v1` |
| `contracts.clauses[].expect.overrides` | `list` | false | `v1` |
| `contracts.clauses[].expect.overrides[].runner` | `string` | true | `v1` |
| `contracts.clauses[].expect.overrides[].status` | `string` | false | `v1` |
| `contracts.clauses[].expect.overrides[].category` | `string` | false | `v1` |
| `contracts.clauses[].expect.overrides[].message_tokens` | `list` | false | `v1` |
| `contracts.clauses[].requires` | `mapping` | false | `v1` |

### Runtime Surface Matrix

| surface | required_keys | catalog |
|---|---|---|
| `harness` | `harness.type`, `harness.profile` | n/a |
| `services[]` | `adapters[].type` (required when `services` is present, or when `contracts.clauses[].bindings.rows[]` / `from: service` imports are used) | `/specs/01_schema/service_contract_catalog_v1.yaml` |
| `contracts.clauses[].bindings.rows[]` | `contracts.clauses[].bindings.rows[].id`, `contracts.clauses[].bindings.rows[].import` | `/specs/01_schema/service_contract_catalog_v1.yaml` |
<!-- GENERATED:END spec_schema_field_catalog -->
