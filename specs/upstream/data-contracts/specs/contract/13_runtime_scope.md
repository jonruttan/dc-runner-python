# Runtime Scope Contract (v1)

Defines the bounded cross-runtime scope for v1 to keep maintenance sustainable.

## Supported Runtimes (v1)

- Rust runner (required blocking lane)
- Python runner (compatibility non-blocking lane)
- PHP runner (compatibility non-blocking lane)
- Node runner (planned compatibility non-blocking lane)
- C runner (planned compatibility non-blocking lane)

Rust is the only required support target for merge/release in v1.

## Scope Constraint

- New runtime support is out of v1 default scope unless explicitly added through:
  - contract/policy updates
  - conformance parity plan
  - governance enforcement updates
  - explicit contract/governance expansion

## Change Bar For Adding A Runtime

To add a runtime to required support:

1. update `specs/contract/08_v1_scope.md`
2. update this runtime scope contract
3. update policy + traceability + governance cases
4. add parity path and deterministic gate evidence
