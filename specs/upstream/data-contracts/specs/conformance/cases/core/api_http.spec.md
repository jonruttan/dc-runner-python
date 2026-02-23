```yaml contract-spec
id: DCCONF-API-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http GET reads relative fixture and exposes body assertions
purpose: Verifies api.http can resolve a local relative request url and assert deterministic
  status and json body shape.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
  - id: assert_2
    assert:
      std.type.json_type:
      - {var: body_json}
      - dict
    imports:
    - from: artifact
      names:
      - body_json
harness:
  check:
    profile: api.http
    config:
      request:
        method: GET
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
```


```yaml contract-spec
id: DCCONF-API-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http requires request.url
purpose: Verifies api.http reports a schema violation when request url is missing from portable
  fixture input.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - api.http request.url is required
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
harness:
  check:
    profile: api.http
    config:
      request:
        method: GET
```


```yaml contract-spec
id: DCCONF-API-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http skip path honors requires.when_missing
purpose: Verifies extension capability gating can skip fixtures when a required capability
  is absent.
type: contract.check
requires:
  capabilities:
  - api.http
  - api.http.missing
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
harness:
  check:
    profile: api.http
    config:
      request:
        method: GET
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
```


```yaml contract-spec
id: DCCONF-API-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http supports POST with body_json
purpose: Verifies practical REST mutating verb support for POST requests in deterministic
  mode.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - body_json
  steps:
  - id: assert_1
    assert:
      std.object.has_key:
      - {var: body_json}
      - id
harness:
  check:
    profile: api.http
    config:
      request:
        method: POST
        url: /specs/03_conformance/cases/fixtures/api_http_created.json
        body_json:
          name: sample
```


```yaml contract-spec
id: DCCONF-API-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http supports PUT
purpose: Verifies practical REST verb support for PUT in deterministic mode.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
harness:
  check:
    profile: api.http
    config:
      request:
        method: PUT
        url: /specs/03_conformance/cases/fixtures/api_http_item_abc-123.json
```


```yaml contract-spec
id: DCCONF-API-006
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http supports PATCH
purpose: Verifies practical REST verb support for PATCH in deterministic mode.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - body_text
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: body_text}
      - abc-123
harness:
  check:
    profile: api.http
    config:
      request:
        method: PATCH
        url: /specs/03_conformance/cases/fixtures/api_http_item_abc-123.json
```


```yaml contract-spec
id: DCCONF-API-007
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http supports DELETE
purpose: Verifies practical REST verb support for DELETE in deterministic mode.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - body_json
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: body_json}
        - deleted
      - true
harness:
  check:
    profile: api.http
    config:
      request:
        method: DELETE
        url: /specs/03_conformance/cases/fixtures/api_http_deleted.json
```


```yaml contract-spec
id: DCCONF-API-008
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http supports HEAD
purpose: Verifies practical REST verb support for HEAD in deterministic mode.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
harness:
  check:
    profile: api.http
    config:
      request:
        method: HEAD
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
```


```yaml contract-spec
id: DCCONF-API-009
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http supports OPTIONS
purpose: Verifies practical REST verb support for OPTIONS in deterministic mode.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
harness:
  check:
    profile: api.http
    config:
      request:
        method: OPTIONS
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
```


```yaml contract-spec
id: DCCONF-API-010
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http rejects unsupported request method
purpose: Verifies unsupported HTTP verbs are rejected as schema violations.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - request.method must be one of
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
harness:
  check:
    profile: api.http
    config:
      request:
        method: TRACE
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
```


```yaml contract-spec
id: DCCONF-API-011
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http preflight requires OPTIONS method
purpose: Verifies cors preflight helper enforces request.method OPTIONS.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - request.cors.preflight requires request.method OPTIONS
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
harness:
  check:
    profile: api.http
    config:
      request:
        method: GET
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
        cors:
          preflight: true
          origin: https://client.example
          request_method: POST
```


```yaml contract-spec
id: DCCONF-API-012
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http scenario executes round-trip requests in order
purpose: Verifies requests scenario supports step templating and exposes steps_json target.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
harness:
  api_http:
    scenario:
      fail_fast: true
  check:
    profile: api.http
    config:
      requests:
      - id: create
        method: POST
        url: /specs/03_conformance/cases/fixtures/api_http_created.json
      - id: get
        method: GET
        url: /specs/03_conformance/cases/fixtures/api_http_item_{{steps.create.body_json.id}}.json
      - id: cleanup
        method: DELETE
        url: /specs/03_conformance/cases/fixtures/api_http_deleted.json
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
  - id: assert_2
    assert:
      std.logic.eq:
      - std.collection.len:
        - {var: steps_json}
      - 3
    imports:
    - from: artifact
      names:
      - steps_json
```


```yaml contract-spec
id: DCCONF-API-013
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http oauth deterministic local token exchange
purpose: Verifies oauth auth profile resolves env refs and produces oauth context metadata
  without network access.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: pass
    category: null
harness:
  api_http:
    mode: deterministic
    auth:
      oauth:
        grant_type: client_credentials
        token_url: /specs/03_conformance/cases/fixtures/oauth_token_ok.json
        client_id_env: PATH
        client_secret_env: HOME
        scope: read:spec
  check:
    profile: api.http
    config:
      request:
        method: GET
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - context_json
  steps:
  - id: assert_1
    assert:
    - std.logic.eq:
      - std.object.get:
        - std.object.get:
          - {var: context_json}
          - meta
        - auth_mode
      - oauth
    - std.logic.eq:
      - std.object.get:
        - std.object.get:
          - {var: context_json}
          - meta
        - oauth_token_source
      - env_ref
```


```yaml contract-spec
id: DCCONF-API-014
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http oauth missing env refs is schema failure
purpose: Verifies oauth env-ref credentials are required and missing env vars fail as schema.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - oauth env var is required
harness:
  api_http:
    auth:
      oauth:
        grant_type: client_credentials
        token_url: /specs/03_conformance/cases/fixtures/oauth_token_ok.json
        client_id_env: SPEC_RUNNER_OAUTH_MISSING_CLIENT_ID
        client_secret_env: SPEC_RUNNER_OAUTH_MISSING_CLIENT_SECRET
  check:
    profile: api.http
    config:
      request:
        method: GET
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
```


```yaml contract-spec
id: DCCONF-API-015
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http oauth invalid auth_style is schema failure
purpose: Verifies oauth auth_style is validated against supported values.
type: contract.check
requires:
  capabilities:
  - api.http
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - auth_style
harness:
  api_http:
    auth:
      oauth:
        grant_type: client_credentials
        token_url: /specs/03_conformance/cases/fixtures/oauth_token_ok.json
        client_id_env: PATH
        client_secret_env: HOME
        auth_style: token
  check:
    profile: api.http
    config:
      request:
        method: GET
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
```


```yaml contract-spec
id: DCCONF-API-016
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http oauth live mode is optional capability
type: contract.check
purpose: Verifies optional live oauth/network execution can be capability-gated and skipped
  in portable lanes.
requires:
  capabilities:
  - api.http
  - api.http.oauth.live
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
harness:
  api_http:
    mode: live
    auth:
      oauth:
        grant_type: client_credentials
        token_url: https://issuer.example.invalid/oauth/token
        client_id_env: OAUTH_CLIENT_ID
        client_secret_env: OAUTH_CLIENT_SECRET
  check:
    profile: api.http
    config:
      request:
        method: GET
        url: https://api.example.invalid/items
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
```


```yaml contract-spec
id: DCCONF-API-017
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: api.http exposes new domain.http helper exports for CORS and steps
purpose: Maintains reference usage for domain.http CORS and scenario helper symbol exports.
type: contract.check
requires:
  capabilities:
  - api.http
  - api.http.domain_lib_refs
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
harness:
  check:
    profile: api.http
    config:
      request:
        method: GET
        url: /specs/03_conformance/cases/fixtures/api_http_ok.json
  use:
  - ref: /specs/05_libraries/domain/http_core.spec.md
    as: lib_http_core_spec
    symbols:
    - domain.http.cors_allow_origin
    - domain.http.cors_allows_header
    - domain.http.cors_allows_method
    - domain.http.cors_credentials_enabled
    - domain.http.cors_max_age_gte
    - domain.http.is_preflight_step
    - domain.http.step_body_json_get
    - domain.http.step_by_id
    - domain.http.step_status_is
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - status
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: status}
      - '200'
```
