# Portable Spec Authoring Contract (v1)

Goal: keep one high-quality executable spec set that is deterministic and
implementation-independent.

## Canonical Spec Set

- The canonical cross-implementation behavior set lives in:
  - `specs/03_conformance/cases/*.spec.md`
- New portable behavior coverage SHOULD be added to this canonical set first.
- Implementation-specific suites (for example `dc-runner-php`) are
  for runner-local coverage and MUST NOT replace portable conformance coverage.

## Conformance Assertion Authoring

- Conformance fixtures MUST use evaluate-only assertion trees for decision semantics.
- Governance executable cases MUST use evaluate-only assertion trees for
  decision semantics.
- Implementation fixture suites SHOULD use evaluate-first assertion trees; sugar
  operators are canonical in `external runner spec repository specs/**` and are only permitted for
  explicitly allowlisted schema-behavior fixtures.
- Sugar operators (`contain`, `regex`, `json_type`, `exists`) remain schema
  syntax for non-governance/non-conformance surfaces only.

## Expected Outcome Shape

- Portable expectations MUST be expressed in `expect.portable`.
- Implementation deltas MUST be expressed only via `expect.overrides[]`
  rows keyed by `runner`.
- Portable semantics should not be duplicated in per-runtime case copies.

## Determinism Requirements

Portable conformance cases SHOULD be deterministic by construction:

- No ambient-time assumptions (`now`, current date/time, timezone-dependent
  expectations) unless the value is injected explicitly as case input.
- No ambient-randomness assumptions unless deterministic seed/input is
  explicitly provided.
- No network dependency in portable cases.
- No ambient environment dependency unless declared via case-level inputs
  (`harness.*`, explicit fixture files, or explicit capability requirements).

Governance enforcement:

- `conformance.no_ambient_assumptions` rejects common ambient
  environment/time/random dependency tokens in portable case content.

## Portability Boundaries

- Portable case IDs use `DCCONF-*`.
- Runtime/implementation-specific behavior should be represented via:
  - `requires.capabilities`
  - `expect.overrides[]`
- Portable case text SHOULD avoid language/runtime branding unless the case is
  explicitly testing portability deltas.

## API Extension Authoring Rule

For `type: api.http` portable cases:

- transport/setup details MUST live under `harness`
- HTTP behavior assertions MUST live under canonical `assert` targets
- portable assertion targets are: `status`, `headers`, `body_text`, `body_json`

## Self-Containment Metric

Portable authoring quality is measured with a portability metric that scores
how self-contained each spec case is versus how implementation-coupled it is.

- The metric scans all canonical `.spec.md` roots and reports:
  - segment scores (`conformance`, `governance`, `impl`, fallback `other`)
  - overall score (case-count-weighted mean)
  - worst-case breakdown with concrete reasons
- Score interpretation:
  - `self_contained_ratio`: `0.0` to `1.0`, higher is better
  - `implementation_reliance_ratio`: `1.0 - self_contained_ratio`
- Phase-v1 policy:
  - metric generation and shape are enforced
  - configured self-containment baseline values are non-regressing (MUST)
  - absolute threshold gating remains deferred until baseline stabilization

## Additional Ratchet Metrics

Governance also tracks complementary ratchet-only metrics that must not regress
from checked-in baselines:

- spec-lang adoption (`spec.spec_lang_adoption_*`)
- runner independence (`runtime.runner_independence_*`)
- docs operability (`docs.operability_*`)
- contract assertions quality (`spec.contract_assertions_*`)

Top-level objective steering is reported through objective scorecard metrics:

- objective scorecard (`objective.scorecard_*`, `objective.tripwires_clean`)
