# Discovery Contract (v1)

## Inputs

- Input is a directory path.
- Runner scans files matching configurable case-file pattern in that
  directory (non-recursive).
- Case-shape schema constraints are sourced from
  `specs/schema/registry/v1/*.yaml` and applied before dispatch.
- Canonical executable case trees are markdown-only and MUST use `.spec.md`:
  - `specs/conformance/cases`
  - `specs/governance/cases`
  - `runner-owned implementation specs`
- Canonical executable case trees MUST NOT include runnable
  `.spec.yaml`/`.spec.yml`/`.spec.json` files.

## Fence Extraction

- Extract fenced blocks using Markdown fence syntax with either:
  - backticks: ```` ``` ```` (3+), or
  - tildes: `~~~` (3+).
- Opening fence info string MUST include:
  - `contract-spec`
  - and one of: `yaml`, `yml`
- Info-string token order is not significant.
- Closing fence MUST use the same fence character as the opener and a fence
  length greater than or equal to the opener.
- Fence body is parsed as YAML.

## Case Shapes

- Fence body MUST decode to either:
  - a mapping (one case), or
  - a list of mappings (many cases).
- Each case MUST include `id` and `type`.
