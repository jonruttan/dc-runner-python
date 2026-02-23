# Conformance Report Format

Conformance reports MUST use a mapping payload:

- `version` (required): `1`
- `results` (required): list of result mappings

Each result mapping MUST include:

- `id`
- `status` (`pass`/`fail`/`skip`)
- `category`
- `message`

Field constraints:

- when `status=pass`: `category` MUST be `null`, `message` MUST be `null`
- when `status=skip`: `category` MUST be `null`, `message` MUST be `null`
- when `status=fail`: `category` MUST be one of `schema|assertion|runtime`
- when `status=fail`: `message` MUST be a non-empty string

Assertion-failure diagnostics SHOULD include context tokens when available:
`case_id`, `assert_path`, and optionally `target`/`op`.

Parity comparison keys:

- required: `id`, `status`, `category`
- optional: token checks against `message` for selected expected cases
