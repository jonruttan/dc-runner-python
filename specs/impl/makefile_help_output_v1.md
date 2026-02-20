# Makefile Help Output Formatting (v1)

This repository uses a global, best-effort formatting policy for `make help`
output across all Makefiles.

## Policy

- `help` output SHOULD be sectioned and aligned for readability.
- `help` output SHOULD use ANSI color when writing to a TTY and color is allowed.
- `help` output MUST fall back to plain text when color is not available or
  explicitly disabled.
- If `NO_COLOR` is set, `help` output MUST not emit ANSI escape codes.
- Formatting is best-effort and MUST NOT change command semantics.

## Scope

- Applies to every `Makefile` in this repository.
- Applies only to human-facing `help` text.
- Does not change any task behavior, flags, or exit codes.

## Compatibility

- Non-interactive environments (CI, redirected output) should remain readable
  without escape-code noise.
- Interactive environments should receive improved visual affordance when
  possible.
