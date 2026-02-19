# Conformance Case Authoring Style

Conformance case docs are authored as Markdown `*.spec.md` files with fenced
`yaml contract-spec` blocks.

Style rules:

- one case per fenced `contract-spec` block
- each block must be immediately preceded by `## <case-id>`
- case ids must be sorted ascending within each file
- each fenced block should stay small (120 lines max) for readability
- each case must include a non-empty `purpose` field describing the intent
- `purpose` should add context beyond `title` (not a copy)
- `purpose` should be at least 8 words and avoid placeholders (`todo`, `tbd`, `fixme`, `xxx`)
- use direct operator-mapping assertions only for conformance decision semantics (`evaluate` wrapper forbidden)
- sugar assertion operators (`contain`, `regex`, `json_type`, `exists`) are
  not allowed in conformance/governance case assertion trees

Purpose lint policy:

- defaults and runtime profiles are configured in `specs/conformance/purpose_lint_v1.yaml`
- per-case override is optional via `purpose_lint` mapping:

## Spec-Lang Expression Layout

Conformance cases MUST keep spec-lang expressions in
operator-keyed mapping AST form for readability and deterministic review diffs.
Use block-first multiline expression formatting for operator trees.
Flow style is reserved for trivial atoms only (for example `{var: subject}`
and short scalar `lit` nodes). Nested operator arguments MUST remain multiline.
Nested `lit` wrappers are forbidden.

Use tooling to enforce/normalize:

- lint: `./scripts/runner_bin.sh spec-lang-lint --cases specs`
- format: `./scripts/runner_bin.sh spec-lang-format --write --cases specs`
- docs sync: `./scripts/runner_bin.sh docs-generate-check`
  - `runtime`: runtime profile name from policy (for example `php`)
  - `min_words`: integer override
  - `placeholders`: list override
  - `forbid_title_copy`: boolean override
  - `severity_by_code`: mapping override (code -> `info|warn|error`)
  - `enabled`: boolean override (when false, skips purpose quality checks; non-empty purpose is still required)

Warning code contract:

- canonical warning code definitions live in `specs/conformance/purpose_warning_codes.md`

Spec-lang lint code contract:

- `SLINT001` evaluate wrapper forbidden (autofixable)
- `SLINT002` nested `lit` wrapper forbidden (autofixable)
- `SLINT003` assertion group key found inside expression context
- `SLINT004` expression leaf must be non-empty operator mapping
- `SLINT005` invalid spec-lang mapping AST expression
- `SLINT006` assert node must be mapping/list
- `SLINT007` contract step `asserts` must be non-empty list
- `SLINT008` prior lowercase group key forbidden (`must`/`can`/`cannot`)
- `SLINT009` assert group must include exactly one group key
- `SLINT010` assert group children must be non-empty list
- `SLINT011` `when` must be mapping
- `SLINT012` unknown `when` hook key
- `SLINT013` `when` hook value must be non-empty list
- `SLINT014` `defines` must be mapping
- `SLINT015` `defines.<scope>` must be mapping
- `SLINT016` `defines` symbol name must be non-empty
- `SLINT017` operator-shaped `lit` wrapper forbidden (autofixable)
- `SLINT018` redundant nested group matches step class (autofixable)
- `SLINT019` nested assert groups forbidden inside step `asserts`
- `SLINT033` `contract.export` case missing `library` metadata
- `SLINT034` `library.stability` must be `alpha|beta|stable|internal`
- `SLINT035` `library` required scalar metadata field is empty
- `SLINT036` `contract.export` must declare non-empty `harness.exports`
- `SLINT039` `harness.exports[].doc` missing or wrong shape
- `SLINT049` `doc.params` names/order mismatch exported params
- `SLINT052` `doc.examples` missing/empty
- `SLINT054` `doc.portability.<runtime>` must be boolean
- `SLINT055` `contract.export` case missing root `doc` metadata
- `SLINT056` root `doc` must be mapping
- `SLINT057` unsupported key in root `doc`
- `SLINT058` missing required root `doc` field for `contract.export`
- `SLINT059` invalid `doc.tags` shape
- `SLINT060` invalid `doc.see_also` shape

Rationale:

- keeps fixtures readable in code review
- keeps diffs small and localized
- keeps case discovery deterministic and predictable
