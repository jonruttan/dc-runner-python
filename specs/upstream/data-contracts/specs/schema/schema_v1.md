# Spec-Test Schema (v1)

This schema defines the stable shape of executable spec tests embedded in
Markdown files selected by case-file pattern (default `*.spec.md`) as fenced blocks:

```text
```yaml contract-spec
...
```

Related docs/reference schemas:

- `specs/schema/docs_schema_v1.md`
- `specs/schema/reference_manifest_v1.md`
- `specs/schema/objective_metrics_schema_v1.md`
- `specs/schema/docs_generator_registry_v1.yaml`
- `specs/schema/docs_layout_profile_v1.yaml`
- `specs/schema/runner_api_catalog_v1.yaml`
- `specs/schema/harness_type_catalog_v1.yaml`
- `specs/schema/spec_lang_builtin_catalog_v1.yaml`
- `specs/schema/spec_lang_stdlib_profile_v1.yaml`
- `specs/schema/subject_profiles_v1.yaml`
- `specs/schema/run_trace_v1.yaml`
- `specs/schema/orchestration_result_v1.yaml`
- `specs/schema/registry_schema_v1.yaml`
- `specs/schema/registry/v1/*.yaml`
- `specs/contract/19_spec_lang_stdlib_profile_v1.md`
- `specs/contract/20_subject_profiles_v1.md`
- `specs/contract/21_schema_registry_contract.md`
- `specs/contract/24_runtime_profiling_contract.md`
```

## Common Fields

- Machine source of truth for case-shape constraints lives in
  `specs/schema/registry/v1/*.yaml`; this document includes a generated
  registry snapshot section.

- `id` (string, required): stable identifier like `CK-CLI-001`
- `spec_version` (int, required): schema major used by this case
- `schema_ref` (string, required): canonical virtual-root schema path
- `type` (string, required): dispatch key (e.g. `cli.run`)
- `title` (string, optional): human description
- `assert_health` (mapping, optional): assertion-health policy override
- `expect` (mapping, optional): conformance outcome expectations
- `requires` (mapping, optional): capability requirements metadata

Parser behavior:

- discovery scans files matching case-file pattern (default `*.spec.md`) in
  the provided directory (non-recursive)
- default discovery is Markdown-only (`*.spec.md`)
- runners MAY opt in additional external case formats via explicit format
  selection (`yaml`, `json`)
- canonical executable spec trees (`specs/conformance/cases`,
  `specs/governance/cases`, `runner-owned implementation specs`) are markdown-only and must
  not include runnable `.spec.yaml`/`.spec.yml`/`.spec.json` files
- fence extraction accepts Markdown fences using either backticks or tildes
  (3+), with info tokens including `contract-spec` and `yaml`/`yml`
- closing fences must use the same fence character and at least the opener
  length
- `type` is required
- `spec_version` is required
- `schema_ref` is required
- `schema_ref` MUST resolve in `/specs/schema/schema_catalog_v1.yaml`
- `spec_version` MUST match the schema major encoded by `schema_ref`

`assert_health`:

- `mode` (string): one of `ignore`, `warn`, `error`
- if omitted, implementations may use a global default (for example env policy)
- policy-driven diagnostics may include redundant sibling assertion branches

`expect` (conformance metadata):

- `portable` (mapping): shared expectation baseline
- `impl` (mapping): per-implementation overlays keyed by runtime name
- expected keys in `portable`/`impl.*`:
  - `status`: `pass`, `fail`, or `skip`
  - `category`: `schema` / `assertion` / `runtime` / `null`
  - `message_tokens`: optional list of expected message tokens
- for conformance fixture cases, `expect.portable` with `status` is required

`requires` (metadata):

- `capabilities` (list[string], optional): declared capabilities for the case
- `when_missing` (string, optional): `skip` or `fail` (default `fail`)

## Portable Authoring Profile

For implementation-independent conformance specs:

- Canonical case set lives in `specs/conformance/cases/**/*.spec.md`.
- Portable expectations are defined in `expect.portable`.
- Runtime deltas are expressed via `expect.impl.<runtime>`.
- Portable cases SHOULD be deterministic and avoid ambient dependency on:
  - time/date/timezone
  - randomness without explicit seeded input
  - network access
  - undeclared environment variables

Normative contract details:

- `specs/contract/06_conformance.md`
- `specs/contract/07_portable_spec_authoring.md`

## Type-Specific Fields

### `type: text.file`

`text.file` asserts against file content.

- If `path` is omitted, the runner asserts against the spec document that
  contains the `yaml contract-spec` block.
- If `path` is provided, it MUST be a relative path and is resolved relative to
  contract root (virtual `/`) and normalized to canonical `/...`.
- Resolved `path` MUST remain within the implementation's configured contract
  root/workspace boundary (path traversal outside that boundary is invalid).

Fields:

- `path` (string, optional): virtual-root path (`/docs/...`) or root-relative
  path string normalized to `/...`

Assertion targets for `text.file`:

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

## `harness` Namespace

Runner-only inputs MUST live under `harness:` to preserve separation of
concerns and keep the spec format portable.

Governance assertion contract:

- For `type: governance.check` cases, decision obligations MUST be encoded in
  `contract` blocks.
- `harness.evaluate` and
  `harness.orchestration_policy.evaluate` are forbidden.
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

- Spec tests are trusted inputs. `cli.run` and hook entrypoints can execute
  project code/commands with runner process privileges.
- Running untrusted spec documents is unsafe and out of scope for v1.
- Implementations MAY pass process environment variables to `cli.run`; keep
  sensitive env values out of runner contexts where possible.
- `data-contracts` is not a sandbox and MUST NOT be presented/documented as one.

For `type: cli.run`, supported `harness` keys include:

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
  `type: orchestration.run`

For `type: api.http`, supported `harness` keys include:

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
- `harness.api_http.auth.oauth` (mapping):
  - `grant_type`: `client_credentials`
  - `token_url`: token endpoint URL or contract path
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
- network `http(s)` token/request URLs require `harness.api_http.mode: live`
- deterministic mode forbids network token/request fetches
- context profile metadata MUST redact secret/token values

`api.http` request shape:

- `request` (mapping) for single-request cases, or `requests` (non-empty list) for scenario cases
- request fields:
  - `method`: `GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS`
  - `url`
  - `headers` (optional mapping)
  - `query` (optional mapping; merged into URL deterministically)
  - `body_text` / `body_json` (mutually exclusive)
  - `cors` (optional mapping):
    - `origin`
    - `request_method` (required when `preflight=true`)
    - `request_headers` (optional list)
    - `preflight` (optional bool, default `false`)

`api.http` additional assert targets:

- `cors_json` (normalized CORS projection for final response)
- `steps_json` (ordered step envelopes in scenario mode)

For `type: docs.generate`, supported `harness` keys include:

- `harness.docs_generate.surface_id` (required)
- `harness.docs_generate.mode` (required): `write|check`
- `harness.docs_generate.output_mode` (required): `markers|full_file`
- `harness.docs_generate.template_path` (required): virtual-root path
- `harness.docs_generate.output_path` (required): virtual-root path
- `harness.docs_generate.marker_surface_id` (required when `output_mode=markers`)
- `harness.docs_generate.data_sources` (required list):
  - `id`
  - `source_type`: `json_file|yaml_file|generated_artifact|command_output`
  - `path` for file/artifact source types
  - `command` for `command_output` source type
- `harness.docs_generate.strict` (optional bool, default `true`)

`setup_files[*].path` constraints:

- MUST be relative
- MUST resolve within the runner temp directory (no path escape)

`harness.spec_lang` fields:

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

`harness.spec_lang.includes` format scope:

- library include paths MAY target `.spec.md`, `.spec.yaml`, or `.spec.yml`
  files
- library include paths use virtual-root semantics (`/` means contract root);
  root-relative values normalize to canonical `/...`
- external references use `external://provider/id` and are deny-by-default
  unless capability and harness policy explicitly allow provider access
- `type: spec.export` producer cases define reusable symbols through
  `harness.exports` entries using `from: assert.function`; function
  bodies are sourced from producer contract-step `asserts` expression mappings
- Canonical export source marker is ``assert.function``.
- default executable case discovery remains Markdown-only (`*.spec.md`) unless
  explicit format opt-in is provided by the runner interface
- executable case types MUST NOT declare `harness.spec_lang.includes`;
  executable symbol loading is chain-first via `harness.chain`

`harness.chain` fields:

- `fail_fast` (bool, optional, default `true`)
- `steps` (list, required when `harness.chain` is present; non-empty)
  - each step:
    - `id` (string, required, unique)
    - `class` (string, required): one of `must`, `can`, `cannot`
    - `ref` (string, required): `[path][#case_id]`
      - path may be virtual-absolute (`/...`) or relative
      - `#case_id` fragment is optional
      - `#case_id` with no preceding path is valid and resolves in current doc
      - case id fragment must match `[A-Za-z0-9._:-]+` when present
      - YAML authors should quote hash-only refs (for example `ref: "#CASE-1"`)
    - `imports` (forbidden non-canonical location)
    - `exports` (forbidden non-canonical location)
    - `allow_continue` (bool, optional, default `false`)
- `exports` (list, optional): producer-owned export declarations
  - each entry:
    - `as` (string, required)
    - `from` (string, required; must be `assert.function`)
    - `path` (string, required for `from: assert.function`)
    - `params` (list[string], optional; non-empty when provided)
    - `required` (bool, optional; default `true`)
  - non-canonical key `from_target` is forbidden
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
- scalar `ref` is the only supported reference format; non-canonical mapping refs are
  invalid.

Chain template interpolation:

- `api.http` request `url`, header values, and `body_text` support
  `{{chain.<step_id>.<export_name>}}` lookups from exported chain state.
- unresolved chain template references are schema/runtime failures.

Documentation generator model:

- docs generation surfaces are declared in
  `specs/schema/docs_generator_registry_v1.yaml`.
- generator-owned markdown sections MUST use read-only markers:
  - `<!-- GENERATED:START surface_id -->`
  - `<!-- GENERATED:END surface_id -->`
- CI/governance check mode MUST verify generated docs artifacts are synchronized.

Implementation note:

- `harness.entrypoint` is required for `cli.run` execution.
- Conformance fixtures SHOULD always set `harness.entrypoint` explicitly.
- Runners MAY provide a safe mode (for example `SPEC_RUNNER_SAFE_MODE=1`) that
  disables hook execution for `cli.run`.
- Runners MAY provide environment allowlisting for subprocess execution (for
  example `SPEC_RUNNER_ENV_ALLOWLIST=K1,K2`).

Assertion targets for `cli.run`:

- `stdout`: text output from command stdout
- `stderr`: text output from command stderr
- `stdout_path`: path printed on first non-empty stdout line
- `stdout_path_text`: UTF-8 text from file at `stdout_path`
- `chain_json`: shared chain state/trace/imports envelope
- `context_json`: JSON subject profile envelope
- `meta_json`: runtime metadata envelope

## Types

Currently supported types:

- `cli.run` (core)
- `text.file` (core)
- `docs.generate` (core extension)
- `orchestration.run` (core extension)

Type contracts live under:

- `specs/contract/types/`

Domain-specific adapters are expected to publish a matching type contract doc
before portable conformance usage.

Published extension type contracts:

- `api.http` (see `specs/contract/types/api_http.md`)

## Assertion Capability Model (Universal Core)

Universal core assertion model:

- every leaf assertion is a spec-lang mapping AST expression.
- every leaf assertion is represented with operator-keyed mappings.
- universal core operator semantics are evaluate-only at runtime.
- evaluator subjects MUST be JSON values only (`null`, boolean, number, string,
  list, object with string keys).

## Assertion Step Shape

`contract` is a mapping with:

- `defaults` (optional mapping)
- `steps` (required list)

Each `steps[]` entry requires:

- `id` (string, unique per case)
- `class` (`MUST` | `MAY` | `MUST_NOT`, default `MUST`)
- `assert` (non-empty expression mapping or list)
- `imports` (optional list)

prior lowercase contract class/group forms (`must`, `can`, `cannot`) are
forbidden.

Forbidden prior forms:

- `contract` list form
- step key `asserts`
- step keys `target` and `on`

Import binding shape:

- `imports` is a list of mapping items
- each item requires `from` and `names`, with optional `as`
- canonical assertion imports are artifact-only (`from: artifact`)
- `names` must be a non-empty list of artifact keys
- `as` is optional mapping `source_name -> local_name`

Import merge behavior:

- effective step imports = `contract.imports` merged with
  `contract.steps[].imports`
- step imports override defaults on key collision

Symbol resolution:

- `{var: subject}` is valid only when `subject` is explicitly imported
- implicit subject/target injection is forbidden in canonical authoring

Supported operators:

- universal core operator: spec-lang v1 operator-keyed mappings at each leaf

Core executable-surface rule:

- `specs/conformance/cases/**/*.spec.md` assertion trees MUST use
  direct spec-lang expression leaves.
- `specs/governance/cases/**/*.spec.md` assertion trees MUST use
  direct spec-lang expression leaves.

Operator constraints:

- all operator values MUST be lists
- each assertion leaf MUST be an expression node using an operator-keyed mapping
- subject reference node: `{var: subject}` resolves via explicit imports
- bare scalar `subject` is a literal string (not a reference)
- spec-lang semantics and budget model are defined in
  `specs/contract/03b_spec_lang_v1.md`
- spec-lang v1 includes deep-equality set algebra (`union`, `intersection`,
  `difference`, `symmetric_difference`, `is_subset`, `is_superset`,
  `set_equals`) and collection transforms (`map`, `filter`, `reduce`, etc.)
  with automatic builtin currying semantics
- spec-lang ramda-style utility surface includes strict numeric math
  (`mul`, `div`, `mod`, `pow`, `abs`, `negate`, `inc`, `dec`, `clamp`,
  `round`, `floor`, `ceil`), comparison/logical helpers (`compare`, `between`,
  `xor`), list utilities (`slice`, `reverse`, `zip`, `zip_with`, `range`,
  `repeat`), object helpers (`keys`, `values`, `entries`, `merge`, `assoc`,
  `dissoc`, `pick`, `omit`), and compositional predicates/combinators
  (`prop_eq`, `where`, `compose`, `pipe`, `identity`, `always`, `replace`,
  `pad_left`, `pad_right`) plus explicit JSON-type predicates (`is_null`,
  `is_bool`/`is_boolean`, `is_number`, `is_string`,
  `is_list`/`is_array`, `is_dict`/`is_object`)
- spec-lang shared library loading rules are defined in
  `specs/contract/14_spec_lang_libraries.md`
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
  `specs/contract/03a_regex_portability_v1.md`

Group constraints:

- `MUST`, `MAY`, and `MUST_NOT` values MUST be lists
- `MUST`, `MAY`, and `MUST_NOT` lists MUST NOT be empty

Canonical negation uses `MUST_NOT`:

```yaml
contract:
  imports:
  - from: artifact
    names: [text]
    as:
      text: subject
  steps:
  - id: assert_no_error
    class: MUST_NOT
    assert:
      std.string.contains:
      - {var: subject}
      - 'ERROR:'
```

Author in canonical form:

- use `MUST` / `MAY` / `MUST_NOT` for boolean groups
- use direct operator mappings in `assert` (no `evaluate` wrapper)
- put every operator value in a list

Example with defaults + step override imports:

```yaml
contract:
  imports:
  - from: artifact
    names: [summary_json]
    as:
      summary_json: subject
  steps:
  - id: assert_passed
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: subject}
        - passed
      - true
  - id: assert_violation_count
    imports:
    - from: artifact
      names: [violation_count]
      as:
        violation_count: subject
    assert:
      std.logic.eq:
      - {var: subject}
      - 0
```

`when` lifecycle hooks (v1):

- optional `when` mapping on executable cases
- non-canonical `harness.on` is forbidden (hard cut)
- allowed keys:
  - `must`
  - `can`
  - `cannot`
  - `fail`
  - `complete`
- each hook key, when present, must be a non-empty list of mapping-AST expressions
- hook expressions evaluate with existing case spec-lang limits/imports/symbols/capabilities
- hook failures are runtime-fatal

Lifecycle order:

- class hooks (`must`/`can`/`cannot`) run after successful clause of
  `MUST`/`MAY`/`MUST_NOT` respectively
- `fail` runs once on first clause or class-hook failure
- `complete` runs only after all clauses and class hooks pass

`contract.job` executable type (v1):

- `type: contract.job`
- required:
  - `harness.jobs` (metadata map)
  - `contract`
- optional:
  - `harness.jobs.<name>.mode`
  - `harness.jobs.<name>.inputs`
  - `harness.jobs.<name>.outputs`

Dispatch contract:

- dispatch is contract-driven using `ops.job.dispatch`
- dispatch metadata is read from `harness.jobs.<name>`
- `harness.job` non-canonical singular form is forbidden
- `ops.job.dispatch` requires `harness.spec_lang.capabilities` to include `ops.job`

Job ref grammar:

- absolute/virtual ref: `/path/to/file.spec.md#CASE-ID`
- same-doc ref: `#CASE-ID` (requires caller-provided document context)
- non-scalar refs are invalid
- missing path/case resolution is schema/runtime error

<!-- BEGIN GENERATED: SCHEMA_REGISTRY_V1 -->

## Generated Registry Snapshot

This section is generated from `specs/schema/registry/v1/*.yaml`.

- profile_count: 7
- top_level_fields: 25
- type_profiles: 3

### Top-Level Keys

| key | type | required | since |
|---|---|---|---|
| `assert_health` | `mapping` | `false` | `v1` |
| `contract` | `any` | `false` | `v1` |
| `doc` | `mapping` | `false` | `v1` |
| `doc.audience` | `string` | `false` | `v1` |
| `doc.description` | `string` | `false` | `v1` |
| `doc.see_also` | `list` | `false` | `v1` |
| `doc.since` | `string` | `false` | `v1` |
| `doc.summary` | `string` | `false` | `v1` |
| `doc.tags` | `list` | `false` | `v1` |
| `domain` | `string` | `false` | `v1` |
| `expect` | `mapping` | `false` | `v1` |
| `harness` | `mapping` | `false` | `v1` |
| `id` | `string` | `true` | `v1` |
| `path` | `string` | `false` | `v1` |
| `purpose` | `string` | `false` | `v1` |
| `requires` | `mapping` | `false` | `v1` |
| `title` | `string` | `false` | `v1` |
| `type` | `string` | `true` | `v1` |
| `when` | `mapping` | `false` | `v1` |
| `when.complete` | `list` | `false` | `v1` |
| `when.fail` | `list` | `false` | `v1` |
| `when.may` | `list` | `false` | `v1` |
| `when.must` | `list` | `false` | `v1` |
| `when.must_not` | `list` | `false` | `v1` |

### Type Profiles

| type | required keys | extra keys |
|---|---|---|
| `contract.check` | `harness`, `contract` | - |
| `contract.export` | `contract`, `harness`, `library`, `doc` | `imports` |
| `contract.job` | `harness`, `contract` | - |

<!-- END GENERATED: SCHEMA_REGISTRY_V1 -->
<!-- GENERATED:START spec_schema_field_catalog -->

## Generated Spec Schema Field Catalog

- top_level_field_count: 25
- type_profile_count: 3
- total_type_field_count: 40

### Top-Level Fields

| key | type | required | since |
|---|---|---|---|
| `assert_health` | `mapping` | false | `v1` |
| `contract` | `any` | false | `v1` |
| `doc` | `mapping` | false | `v1` |
| `doc.audience` | `string` | false | `v1` |
| `doc.description` | `string` | false | `v1` |
| `doc.see_also` | `list` | false | `v1` |
| `doc.since` | `string` | false | `v1` |
| `doc.summary` | `string` | false | `v1` |
| `doc.tags` | `list` | false | `v1` |
| `domain` | `string` | false | `v1` |
| `expect` | `mapping` | false | `v1` |
| `harness` | `mapping` | false | `v1` |
| `id` | `string` | true | `v1` |
| `path` | `string` | false | `v1` |
| `purpose` | `string` | false | `v1` |
| `requires` | `mapping` | false | `v1` |
| `title` | `string` | false | `v1` |
| `type` | `string` | true | `v1` |
| `when` | `mapping` | false | `v1` |
| `when.complete` | `list` | false | `v1` |
| `when.fail` | `list` | false | `v1` |
| `when.may` | `list` | false | `v1` |
| `when.must` | `list` | false | `v1` |
| `when.must_not` | `list` | false | `v1` |

### Type Profiles

| case_type | field_count | required_top_level |
|---|---|---|
| `contract.check` | 5 | `harness`, `contract` |
| `contract.export` | 28 | `contract`, `harness`, `library`, `doc` |
| `contract.job` | 7 | `harness`, `contract` |
<!-- GENERATED:END spec_schema_field_catalog -->
