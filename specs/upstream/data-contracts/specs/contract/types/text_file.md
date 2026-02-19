# Type Contract: text.file

## Status

- v1 core type

## Purpose

Assert text content from the containing spec document or an explicit contract-root path.

## Required Fields

- `id` (string)
- `type` (must equal `text.file`)
- `assert` (assertion tree)

## Optional Fields

- `path` (string, virtual-root `/...` or root-relative normalized to `/...`)
- common optional fields from schema v1 (`title`, `assert_health`, `expect`, `requires`, `harness`)

## Targets

- `text`
- `context_json`

Subject semantics:

- `text`: UTF-8 text from containing spec document or resolved relative path.
- `context_json`: JSON subject profile envelope for `text.file/v1`.

## Type Rules

- when `path` is omitted, target subject is the containing spec document
- when `path` is present, it resolves against contract root virtual `/`
- resolved `path` MUST remain inside configured contract root

## Failure Category Guidance

- schema violations -> `schema`
- assertion mismatches -> `assertion`
- unexpected runtime faults -> `runtime`
