# Docs Metadata Schema (v1)

This schema defines machine-checkable documentation metadata for the reference
manual surface.

`doc-meta` may be declared in either:

- markdown front matter (`--- ... ---`)
- fenced block with `yaml doc-meta`

Example:

```yaml doc-meta
doc_id: DOC-REF-001
title: Chapter title
status: active
audience: implementer
owns_tokens:
- token_a
requires_tokens:
- token_b
commands:
- run: ./scripts/ci_gate.sh
  purpose: Execute local gate.
examples:
- id: EX-REF-001
  runnable: true
sections_required:
- '## Purpose'
- '## Inputs'
- '## Outputs'
- '## Failure Modes'
```

Required keys:

- `doc_id` (string): `DOC-<AREA>-###`
- `title` (string, non-empty)
- `status` (`active` | `draft`)
- `audience` (`operator` | `integrator` | `implementer` | `maintainer` | `governance` | `reviewer` | `auditor`, default `implementer`)
- `owns_tokens` (list[string])
- `requires_tokens` (list[string])
- `commands` (list[mapping `{run, purpose}`])
- `examples` (list[mapping `{id, runnable, opt_out_reason?}`])
- `sections_required` (list[string], non-empty)

Rules:

- `examples[*].id` MUST match `EX-<...>` style identifier.
- `examples[*].runnable` MUST be boolean.
- `examples[*].opt_out_reason` MUST be non-empty when `runnable: false`.
- `sections_required` tokens are matched case-insensitively in document text.
