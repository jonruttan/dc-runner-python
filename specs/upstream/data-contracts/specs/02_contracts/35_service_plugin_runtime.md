# Service Plugin Runtime Contract (v1)

Defines the portable runtime boundary between core runner orchestration and
service-specific integration implementations.

## Purpose

- Keep integration behavior in service implementations (for example HTTP client
  behavior in `io.http` service implementation).
- Keep core runner responsible for orchestration only.
- Support both built-in and runtime-loaded plugin packaging.

## Packaging Modes

- Built-in: service implementation linked into runner distribution.
- Plugin: service implementation loaded at runtime from signed and lock-pinned
  plugin artifacts.

Both modes MUST provide equivalent behavior for the same service
`type/profile/import` contract.

## Plugin Manifests and Locks

- Manifest schema: `/specs/01_schema/service_plugin_manifest_v1.yaml`
- Lock schema: `/specs/01_schema/service_plugin_lock_v1.yaml`

Runtime-loaded plugins MUST be both:

- digest-pinned in lock data
- signature-verified before execution

## Process RPC Protocol Lifecycle

Canonical out-of-process method lifecycle:

1. `plugin.initialize`
2. `service.validate_config`
3. `service.list_imports`
4. `service.invoke`
5. `plugin.shutdown`

Transport is JSON-RPC over stdio.

## Core Runner Responsibilities

- Resolve service action by exact `type/profile`.
- Enforce lock/signature policy for runtime-loaded plugins.
- Validate declared service imports against resolved implementation surface.
- Keep artifact-id I/O routing and binding merge semantics deterministic.
- Normalize plugin failures into canonical runtime errors.

## Service Implementation Responsibilities

- Own service-specific integration libraries and behavior.
- Validate service config shape for supported profiles.
- Expose profile-scoped callable import names.
- Execute service invocation contract and return structured results.

## Failure Behavior

Hard-fail conditions include:

- unresolved service implementation for action `type/profile`
- lock/signature/digest verification failure
- plugin API version mismatch
- declared import unavailable for resolved implementation profile
- protocol transport failure or timeout

Errors MUST be direct and actionable.
