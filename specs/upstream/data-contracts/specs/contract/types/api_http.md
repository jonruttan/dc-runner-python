# Type Contract: api.http

## Status

- published extension type contract (not in v1 core set)

## Purpose

Define portable REST endpoint checks with deterministic defaults, CORS-aware response projection, and optional scenario round-trip orchestration.

## Required Fields

- `id` (string)
- `type` (must equal `api.http`)
- one of:
  - `request` (mapping) for single-request mode
  - `requests` (non-empty list[mapping]) for scenario mode
- `assert` (assertion tree)

## Request Model

`request` and each `requests[*]` step support:

- `id` (required in `requests[*]`, unique per case)
- `method` (required): one of `GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS`
- `url` (required): URL or contract path (`/` = contract root)
- `headers` (optional mapping[string,string])
- `body_text` (optional string)
- `body_json` (optional mapping/list/scalar JSON)
- `query` (optional mapping) merged into URL deterministically
- `cors` (optional mapping):
  - `origin` (optional string)
  - `request_method` (required when `preflight=true`)
  - `request_headers` (optional list[string])
  - `preflight` (optional bool, default `false`)

Rules:

- `body_text` and `body_json` are mutually exclusive.
- CORS preflight requires `method: OPTIONS`.
- `request.cors` is the canonical CORS helper node.

## Harness Model

`harness.api_http` (optional):

- `mode`: `deterministic|live` (default `deterministic`)
- `auth.oauth` (optional mapping):
  - `grant_type`: `client_credentials`
  - `token_url`
  - `client_id_env`
  - `client_secret_env`
  - `scope` (optional)
  - `audience` (optional)
  - `auth_style`: `basic|body` (default `basic`)
  - `token_field` (default `access_token`)
  - `expires_field` (default `expires_in`)
  - `refresh_skew_seconds` (default `30`)
- `scenario` (optional mapping):
  - `setup` (optional):
    - `command` (required list[string])
    - `cwd` (optional virtual-root path)
    - `env` (optional mapping[string,string])
    - `ready_probe` (optional):
      - `url` (required)
      - `method` (optional, default `GET`)
      - `expect_status_in` (optional list[int], default `[200,204]`)
      - `timeout_ms` (optional, default `10000`)
      - `interval_ms` (optional, default `200`)
  - `teardown` (optional):
    - `command` (required list[string])
    - `cwd` / `env` optional
  - `fail_fast` (optional bool, default `true`)

Canonical lifecycle key: `harness.api_http.scenario`.

## Scenario Templating

In scenario mode (`requests`), `url`, header values, and `body_text` support moustache step substitution:

- `{{steps.<id>.status}}`
- `{{steps.<id>.body_json.<field>}}`

## Targets

- `status`
- `headers`
- `body_text`
- `body_json`
- `cors_json`
- `steps_json`
- `context_json`

Target semantics:

- In scenario mode, `status|headers|body_text|body_json|cors_json` target the final step.
- `steps_json` provides ordered step result envelopes.
- `context_json` is `api.http/v1` profile and includes scenario + OAuth metadata.

## Type Rules

- Transport/setup details MUST live under `harness`.
- Portable behavior assertions MUST use canonical `assert` groups/operators.
- network URLs (`http://` / `https://`) require `harness.api_http.mode: live`.
- OAuth credentials are env-ref only (`*_env`); inline secret literals are forbidden.
- context metadata MUST redact token/secret values.

## Conformance Notes

- `api.http` is an extension type and not required for v1 core conformance.
- Implementations advertising shared `api.http` capability MUST produce matching status/category outcomes for shared fixtures.
