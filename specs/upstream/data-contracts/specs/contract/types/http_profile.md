# HTTP Subject Profile Contract

HTTP adapter responses MUST be projected to JSON subject envelopes.

Projection rules:

- `value.status` -> integer
- `value.headers` -> JSON object mapping string to string
- `value.body_text` -> string
- `value.body_json` -> parsed JSON value or `null`
- `value.cors` -> normalized CORS projection:
  - `allow_origin`
  - `allow_methods` (list[string])
  - `allow_headers` (list[string])
  - `expose_headers` (list[string])
  - `allow_credentials` (bool|null)
  - `max_age` (int|null)
  - `vary_origin` (bool)
- `meta.auth_mode` -> `none` | `oauth`
- `meta.oauth_token_source` -> `none` | `env_ref`
- `context.oauth` -> metadata-only OAuth details:
  - `token_url_host`
  - `scope_requested`
  - `token_fetch_ms`
  - `used_cached_token`
- `context.scenario` (scenario mode):
  - `setup_started`
  - `setup_ready`
  - `teardown_ran`
  - `step_count`
  - `step_ids`
- `context.steps` -> ordered list of per-step envelopes

Redaction rule:

- raw bearer tokens and secrets MUST NOT appear in context/profile diagnostics.

Profile id: `api.http/v1`.
