# Design Goals (v1)

These are cross-language design goals for `data-contracts`. Contract and schema
changes SHOULD be evaluated against this list.

Project-level philosophy and process bar:
`docs/design_philosophy.md`.

## Determinism

- Same spec inputs MUST produce the same pass/fail outcomes.
- Behavior MUST NOT depend on ambient state unless explicitly declared:
  - wall clock time
  - randomness
  - host locale
  - undeclared env vars
  - undeclared network access
- Discovery and execution order SHOULD be deterministic.

## Portability

- DSL semantics MUST be language-neutral.
- Canonical contract docs are the source of truth; implementation docs are
  explanatory.
- Conformance fixtures MUST be runnable by each implementation.

## DSL Clarity

- Each DSL meaning SHOULD have one canonical expression.
- Ambiguous aliases/shorthand SHOULD be rejected, not auto-rewritten.
- Validation errors MUST be early and actionable.

## Assertion Health

- Runner SHOULD detect assertions likely to be brittle, vacuous, or misleading.
- The system SHOULD support policy control to escalate findings:
  - ignore
  - warn
  - error
- Policy SHOULD be configurable at both:
  - global runner level
  - per-spec/per-test level
- Health checks SHOULD focus on concrete anti-patterns, for example:
  - always-true/always-false group constructs
  - contradictory or vacuous conditions
  - brittle regex/text checks with high incidental coupling

## Operability

- Failures SHOULD include case id and assertion path context.
- Machine-readable reporting SHOULD be stable across implementations.
- Contract-breaking changes MUST be versioned and documented.

## Minimal Reusable Parts

- The project SHOULD be composed of a minimal set of reusable boundaries:
  - schema/contract
  - spec-lang decision core
  - adapter side-effect surfaces
- New behavior SHOULD prefer reusing existing contract/type/config surfaces over
  adding one-off runtime-specific paths.

## Meta Self-Application

- The project SHOULD enforce its own contract/governance policy through
  executable specs and governance checks.
- Governance decision logic SHOULD be data-driven (spec-lang policies) rather
  than ad-hoc host-language branches.
