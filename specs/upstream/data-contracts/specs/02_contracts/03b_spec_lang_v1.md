# Spec-Lang v1 Contract

## Scope

`spec-lang` is an expression DSL used through the
assertion leaf operator `evaluate`.
Assertion group semantics (`must`, `can`, `cannot`) are defined by the
assertion contract and host this expression language.

YAML authoring encoding is operator-keyed mapping AST form.
Implementations compile this mapping AST to internal list-token form before
evaluation.

```yaml
fn:
- [arg1, arg2]
- {eq: [{var: arg1}, {var: arg2}]}
```

No string parser and no implementation-defined extension hooks are part of v1.

Stdlib completeness source of truth:

- `/specs/01_schema/spec_lang_stdlib_profile_v1.yaml`
- `/specs/02_contracts/19_spec_lang_stdlib_profile_v1.md`

Runtime requirement:

- Core stdlib symbols are deterministic/pure unless explicitly marked
  effectful in the stdlib profile contract.
- Effectful symbols MUST be capability-gated.
- `ops.os.*` symbols require explicit `harness.spec_lang.capabilities: [ops.os]`.
- Subjects consumed by the evaluator MUST be JSON-core values only; native
  runtime values must be projected into JSON profile envelopes.

Ops namespace:

- `ops.*` symbols use deep-dot hierarchy:
  `ops.<segment>(.<segment>)+` (for example `ops.fs.file.read`,
  `ops.proc.command.exec`, `ops.fs.path.normalize`).
- `ops.fs.*` utilities are pure/deterministic helpers.
- `ops.os.*` symbols are effectful and capability-gated.
- `ops.job.dispatch` is effectful and capability-gated (`ops.job`).
- underscore shorthand forms are invalid.

## Core Forms

Boolean:

- `and`
- `or`
- `not`

Value/text:

- `contains`
- `starts_with`
- `ends_with`
- `eq`
- `neq`
- `in`

JSON/value:

- `json_type`
- `is_null`
- `is_bool`
- `is_boolean`
- `is_number`
- `is_string`
- `is_list`
- `is_array`
- `is_dict`
- `is_object`
- `has_key`
- `get`

`json_type` accepts canonical JSON names (`null`, `boolean`, `number`,
`string`, `array`, `object`) and normalized internal names (`bool`, `list`,
`dict`).

Utility:

- `subject`
- `len`
- `count`
- `first`
- `rest`
- `trim`
- `lower`
- `upper`
- `split`
- `join`
- `map`
- `filter`
- `reject`
- `find`
- `reduce`
- `partition`
- `group_by`
- `uniq_by`
- `flatten`
- `concat`
- `append`
- `prepend`
- `take`
- `drop`
- `slice`
- `reverse`
- `zip`
- `zip_with`
- `range`
- `repeat`
- `any`
- `all`
- `none`
- `sum`
- `min`
- `max`
- `sort_by`
- `pluck`
- `keys`
- `values`
- `entries`
- `merge`
- `assoc`
- `dissoc`
- `pick`
- `omit`
- `distinct`
- `is_empty`
- `coalesce`
- `matches_all`
- `var`
- `add`
- `sub`
- `mul`
- `div`
- `mod`
- `pow`
- `abs`
- `negate`
- `inc`
- `dec`
- `clamp`
- `round`
- `floor`
- `ceil`
- `compare`
- `between`
- `xor`
- `prop_eq`
- `where`
- `compose`
- `pipe`
- `identity`
- `always`
- `replace`
- `pad_left`
- `pad_right`
- `json_parse`
- `regex_match`
- `matches`
- `lt`
- `lte`
- `gt`
- `gte`
- `equals`
- `includes`
- `union`
- `intersection`
- `difference`
- `symmetric_difference`
- `is_subset`
- `is_superset`
- `set_equals`

Filesystem utility (pure, metadata-only):

- `ops.fs.path.normalize`
- `ops.fs.path.join`
- `ops.fs.path.split`
- `ops.fs.path.dirname`
- `ops.fs.path.basename`
- `ops.fs.path.extname`
- `ops.fs.path.stem`
- `ops.fs.path.is_abs`
- `ops.fs.path.has_ext`
- `ops.fs.path.change_ext`
- `ops.fs.path.relativize`
- `ops.fs.path.common_prefix`
- `ops.fs.path.parents`
- `ops.fs.path.within`
- `ops.fs.path.compare`
- `ops.fs.path.sort`
- `ops.fs.file.exists`
- `ops.fs.file.is_file`
- `ops.fs.file.is_dir`
- `ops.fs.file.size_bytes`
- `ops.fs.file.path`
- `ops.fs.file.name`
- `ops.fs.file.parent`
- `ops.fs.file.ext`
- `ops.fs.file.get`
- `ops.fs.json.parse`
- `ops.fs.json.get`
- `ops.fs.json.get_or`
- `ops.fs.json.has_path`
- `ops.fs.glob.match`
- `ops.fs.glob.filter`
- `ops.fs.glob.any`
- `ops.fs.glob.all`

OS/system utility (capability-gated):

- `ops.os.exec`
- `ops.os.exec_capture`
- `ops.os.env_get`
- `ops.os.env_has`
- `ops.os.cwd`
- `ops.os.pid`
- `ops.os.sleep_ms`
- `ops.os.exit_code`
- `ops.helper.call`

Recursion/control:

- `let`
- `fn`
- `call`
- `if`

## Equality + Set Algebra Semantics

- `equals` uses deep structural equality:
  - scalars compare by strict type+value
  - lists compare by length + ordered pairwise equality
  - maps compare by key-set equality + per-key value equality
- set operators (`union`, `intersection`, `difference`,
  `symmetric_difference`) require list inputs.
- set outputs are deterministic and preserve stable left-first encounter order.
- `includes` performs list membership using deep equality.
- `set_equals` compares de-duplicated deep-equality sets (order-insensitive).
- `is_subset` / `is_superset` apply the same de-duplicated deep-equality model.

## Currying Contract

- Builtins MUST support automatic currying by declared arity.
- Supplying fewer args than arity MUST return a callable builtin function value.
- Supplying exactly arity args MUST evaluate the builtin.
- Supplying extra args MUST:
  - evaluate first arity args
  - apply remaining args only if the intermediate result is callable
  - otherwise fail as `schema` with deterministic over-application diagnostics
- Function values MUST be usable via `call` and as inputs to collection forms
  (for example `map`, `filter`, `reduce`).

## Tail Position and TCO

Tail positions:

- the selected branch expression of `if`
- the body expression of `let`
- the body of `fn` when entered by `call`

Contract requirements:

- Evaluators MUST implement proper tail-call optimization for tail-position
  `call`.
- Tail-recursive programs MUST NOT fail due to host call-stack depth.
- Evaluators MUST execute with an explicit iterative state/trampoline model
  rather than host recursion for tail calls.

Non-tail recursion is not guaranteed stack-safe and may fail by evaluator
budget limits.

## Evaluator Budget Model

Evaluators MUST enforce all budgets:

- `max_steps`
- `max_nodes`
- `max_literal_bytes`
- optional `timeout_ms`

Budget failures are runtime failures and MUST identify the exceeded budget key:

- `steps`
- `nodes`
- `literal_size`
- `timeout`

## Error Semantics

- malformed expression, unknown symbol, arity/type error: `schema`
- expression evaluates false under `must`: `assertion`
- evaluator timeout/budget/internal execution fault: `runtime`

Diagnostics SHOULD include:

- case id
- assertion path
- failing symbol or form
- budget exceeded reason when applicable

## Harness Configuration

Runners MAY accept evaluator budget overrides in harness config:

```yaml
harness:
  spec_lang:
    max_steps: 20000
    max_nodes: 20000
    max_literal_bytes: 262144
    timeout_ms: 200
```

All values are integers; `timeout_ms` MAY be `0` to disable timeout enforcement.

Library configuration (optional):

```yaml
harness:
  spec_lang:
    includes:
    - /specs/05_libraries/common.spec.md
    imports:
    - /is_portable_case
```

Library contract details:

- `specs/02_contracts/14_spec_lang_libraries.md`
- `includes` supports `.spec.md`, `.spec.yaml`, and `.spec.yml` includes
  while executable case discovery remains Markdown-default unless explicitly
  opted in by runner interface flags
- `functions.<symbol>` in `type: spec_lang.export` cases uses mapping-AST
  authoring (list s-expr authoring is invalid)

## Canonical Authoring Format

For readability and deterministic diffs, implementations in this repo
standardize `evaluate` expression formatting to:

- one operator-keyed mapping expression per `evaluate` list entry
- explicit list args for operators in mapping form
- canonical subject reference form is explicit:
  `{var: subject}` resolves only when `subject` is explicitly imported in contract step imports/defaults
- `lit` wrapper for collection literal nodes
- bare scalar `subject` is a literal string (not a special form)
- condensed inline args for short forms (for example
  `eq: [{add: [1, 2]}, 3]`) where readability improves
- nested mapping AST layout for larger expressions (not list S-expression
  authoring)

Tooling:

- lint: `./scripts/control_plane.sh spec-lang-format --check --cases specs`
- format: `./scripts/control_plane.sh spec-lang-format --write --cases specs`
