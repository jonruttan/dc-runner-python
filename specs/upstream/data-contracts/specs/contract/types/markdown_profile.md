# Markdown Subject Profile Contract (v1)

Markdown checks use JSON projection surfaces and library-backed predicates.

Projection rules:

- source text MAY be provided directly as a string subject
- or as a profile envelope mapping with:
  - `value` (string markdown text)
  - `meta` (mapping, optional)
  - `context` (mapping, optional structured markdown facts)

Dual-input contract:

- helpers in `/specs/05_libraries/domain/markdown_core.spec.md` MUST accept:
  - raw markdown text string subjects
  - markdown profile envelope mapping subjects
- when neither a string nor a mapping envelope is provided, evaluation is a
  schema error.

Recommended `context` keys for structured checks:

- `headings`: list of `{text, level}`
- `heading_positions`: mapping `heading_text -> ordinal`
- `links`: list of `{target, resolved}`
- `tokens`: mapping `token -> bool|mapping`
- `token_owners`: mapping `token -> list[path]`
- `token_dependencies`: list of `{token, depends_on, resolved}`

Profile id: `markdown.generic/v1`.
