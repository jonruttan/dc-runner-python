# Control Plane Runtime Separation Contract (v1)

Defines repository-boundary separation between the `data-contracts` control plane
and external runtime implementations.

## Normative Separation

- `data-contracts` is authoritative for contracts, schemas, governance, and docs.
- runtime execution and implementation verification are owned by runner repos.
- this repository evaluates runtime status telemetry; it does not execute runtime
  implementation lanes as canonical CI requirements.

## Required Control-Plane Outcomes

- status exchange contracts and schemas remain valid and versioned.
- runner status matrix artifacts are emitted in CI.
- compatibility telemetry freshness policy is enforced.
- docs and contract surfaces remain coherent and discoverable.

## Non-Goals

- runtime implementation tests in this repository
- implementation-specific optimization, profiling, or benchmark ownership
- implementation-owned command behavior conformance testing in this repository
