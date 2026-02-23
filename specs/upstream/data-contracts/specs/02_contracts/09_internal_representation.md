# Internal Representation Contract (v1)

## Purpose

`data-contracts` decouples external case authoring formats from execution by
compiling cases into a single internal representation before dispatch/runtime
evaluation.

## Internal Model

Each compiled case contains:

- `id`
- `type`
- `title` (optional)
- `doc_path` (source location)
- `harness` (runner-only config mapping)
- `raw_case` (original external mapping for compatibility/tooling)
- `metadata` (expect/requires/source)
- `assert_tree` (compiled internal clause/predicate assertion tree)

Internal assertion node forms:

- group node:
  - `op`: `must` | `can` | `cannot`
  - `target`: optional inherited target
  - `children`: child internal nodes
  - `assert_path`: stable path for diagnostics
- predicate leaf:
  - `target`
  - `subject_key` (adapter-provided subject lookup key)
  - `op` (original external op token for diagnostics)
  - `expr` (spec-lang expression)
  - `assert_path`

## External -> Internal Compile Rules

- universal core: `evaluate` (pass-through spec-lang expression)

List-valued leaf ops compile to conjunction semantics (same as current v1
external behavior).

## Discovery and Codec Rules

Default discovery remains `.spec.md` only with one suite fence.

Opt-in external formats:

- `.spec.yaml` / `.spec.yml`
- `.spec.json`

The compile contract is semantic-lossless:

- case ids must remain stable
- suite defaults must be shallow-merged into each expanded contract item
- pass/fail/category behavior must remain equivalent
- formatting/comments are not guaranteed to round-trip

## Compatibility Rules

- Canonical authoring for specs fixtures remains `.spec.md`.
- External codecs are adapters; they must not change runtime semantics.
- Non-core custom runners may still receive external-case objects for
  compatibility; core runner types execute compiled internal cases.
- Conformance and governance executable case assertion trees are evaluate-only
  at authoring level; non-`evaluate` leaf operators are not allowed in these
  core surfaces.

## Assertion Execution Invariant

MUST:

- runtime assertion execution MUST evaluate compiled spec-lang predicates.
- external leaf operators MUST be evaluate expressions before execution.
- runners MUST NOT introduce direct ad-hoc leaf-op execution branches that
  bypass the spec-lang evaluator.
- spec-lang evaluator MUST remain pure; side-effectful probes are adapter
  responsibilities that produce normalized subject values.
- operator applicability MUST be governed by subject availability/shape
  contracts, not hidden per-type runtime allowlists.
