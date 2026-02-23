# Runner CLI Interface Contract (v1)

Defines the portable CLI surface shared by runner implementations and consumed
by the control-plane conformance layer.

## Scope

This contract specifies only implementation-agnostic runner CLI behavior.
Runtime-specific or implementation-specific subcommands remain runner-owned.

## MUST Surface

Runner CLIs MUST provide deterministic behavior for:

- `runner --help`
- `runner conformance`
- `runner governance`
- unknown command handling with non-zero exit code
- structured status output mode (`--json` or equivalent capability)

## MAY Surface

Runner CLIs MAY provide:

- implementation-specific helper subcommands
- additional diagnostics modes
- additional output formats beyond the structured mode

## Capability Model

Portable required behavior is represented as required commands and output
contract keys in `/specs/01_schema/runner_cli_contract_v1.yaml`.

Implementation-specific additions MUST be capability-gated and MUST NOT weaken
the required portable command semantics.
