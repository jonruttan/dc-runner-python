```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-API-001
    title: api.http GET reads relative fixture and exposes body assertions
    purpose: Verifies api.http can resolve a local relative request url and assert
      deterministic status and json body shape.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.1
        service: svc.assert_check.api_http.1
        outputs:
        - to: body_json
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
      - id: assert_2
        assert:
          std.type.json_type:
          - var: body_json
          - dict
        imports:
        - from: artifact
          names:
          - body_json
  - id: DCCONF-API-002
    title: api.http requires request.url
    purpose: Verifies api.http reports a schema violation when request url is missing
      from portable fixture input.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - api.http request.url is required
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.2
        service: svc.assert_check.api_http.2
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-003
    title: api.http skip path honors requires.when_missing
    purpose: Verifies extension capability gating can skip fixtures when a required
      capability is absent.
    expect:
      portable:
        status: skip
        category:
    requires:
      capabilities:
      - api.http
      - api.http.missing
      when_missing: skip
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.3
        service: svc.assert_check.api_http.3
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-004
    title: api.http supports POST with body_json
    purpose: Verifies practical REST mutating verb support for POST requests in deterministic
      mode.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.4
        service: svc.assert_check.api_http.4
        outputs:
        - to: body_json
    asserts:
      imports:
      - from: artifact
        names:
        - body_json
      checks:
      - id: assert_1
        assert:
          std.object.has_key:
          - var: body_json
          - id
  - id: DCCONF-API-005
    title: api.http supports PUT
    purpose: Verifies practical REST verb support for PUT in deterministic mode.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.5
        service: svc.assert_check.api_http.5
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-006
    title: api.http supports PATCH
    purpose: Verifies practical REST verb support for PATCH in deterministic mode.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.6
        service: svc.assert_check.api_http.6
        outputs:
        - to: body_text
    asserts:
      imports:
      - from: artifact
        names:
        - body_text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: body_text
          - abc-123
  - id: DCCONF-API-007
    title: api.http supports DELETE
    purpose: Verifies practical REST verb support for DELETE in deterministic mode.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.7
        service: svc.assert_check.api_http.7
        outputs:
        - to: body_json
    asserts:
      imports:
      - from: artifact
        names:
        - body_json
      checks:
      - id: assert_1
        assert:
          std.logic.eq:
          - std.object.get:
            - var: body_json
            - deleted
          - true
  - id: DCCONF-API-008
    title: api.http supports HEAD
    purpose: Verifies practical REST verb support for HEAD in deterministic mode.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.8
        service: svc.assert_check.api_http.8
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-009
    title: api.http supports OPTIONS
    purpose: Verifies practical REST verb support for OPTIONS in deterministic mode.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.9
        service: svc.assert_check.api_http.9
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-010
    title: api.http rejects unsupported request method
    purpose: Verifies unsupported HTTP verbs are rejected as schema violations.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - request.method must be one of
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.10
        service: svc.assert_check.api_http.10
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-011
    title: api.http preflight requires OPTIONS method
    purpose: Verifies cors preflight helper enforces request.method OPTIONS.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - request.cors.preflight requires request.method OPTIONS
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.11
        service: svc.assert_check.api_http.11
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-012
    title: api.http scenario executes round-trip requests in order
    purpose: Verifies requests scenario supports step templating and exposes steps_json
      target.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.12
        service: svc.assert_check.api_http.12
        outputs:
        - to: status
        - to: steps_json
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
      - id: assert_2
        assert:
          std.logic.eq:
          - std.collection.len:
            - var: steps_json
          - 3
        imports:
        - from: artifact
          names:
          - steps_json
  - id: DCCONF-API-013
    title: api.http oauth deterministic local token exchange
    purpose: Verifies oauth auth profile resolves env refs and produces oauth context
      metadata without network access.
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.13
        service: svc.assert_check.api_http.13
        outputs:
        - to: context_json
    asserts:
      imports:
      - from: artifact
        names:
        - context_json
      checks:
      - id: assert_1
        assert:
        - std.logic.eq:
          - std.object.get:
            - std.object.get:
              - var: context_json
              - meta
            - auth_mode
          - oauth
        - std.logic.eq:
          - std.object.get:
            - std.object.get:
              - var: context_json
              - meta
            - oauth_token_source
          - env_ref
  - id: DCCONF-API-014
    title: api.http oauth missing env refs is schema failure
    purpose: Verifies oauth env-ref credentials are required and missing env vars
      fail as schema.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - oauth env var is required
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.14
        service: svc.assert_check.api_http.14
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-015
    title: api.http oauth invalid auth_style is schema failure
    purpose: Verifies oauth auth_style is validated against supported values.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - auth_style
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.15
        service: svc.assert_check.api_http.15
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-016
    title: api.http oauth live mode is optional capability
    purpose: Verifies optional live oauth/network execution can be capability-gated
      and skipped in portable lanes.
    expect:
      portable:
        status: skip
        category:
    requires:
      capabilities:
      - api.http
      - api.http.oauth.live
      when_missing: skip
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.16
        service: svc.assert_check.api_http.16
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
  - id: DCCONF-API-017
    title: api.http exposes new domain.http helper exports for CORS and steps
    purpose: Maintains reference usage for domain.http CORS and scenario helper symbol
      exports.
    expect:
      portable:
        status: skip
        category:
    requires:
      capabilities:
      - api.http
      - api.http.domain_lib_refs
      when_missing: skip
    bindings:
      defaults:
        import: pipe_identity
        mode: merge
      rows:
      - id: bind.api_http.17
        service: svc.assert_check.api_http.16
        outputs:
        - to: status
    asserts:
      imports:
      - from: artifact
        names:
        - status
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: status
          - '200'
adapters:
- type: io.http
  defaults:
    direction: input
    imports:
    - names:
      - pipe_identity
    profile: request.http
  actions:
  - id: svc.assert_check.api_http.1
    config:
      request:
        method: GET
        artifact_id: art.svc.assert_check.api_http.1.request_url.1
  - id: svc.assert_check.api_http.2
    config:
      request:
        method: GET
  - id: svc.assert_check.api_http.3
    config:
      request:
        method: POST
        body_json:
          name: sample
        artifact_id: art.svc.assert_check.api_http.3.request_url.1
  - id: svc.assert_check.api_http.4
    config:
      request:
        method: PUT
        artifact_id: art.svc.assert_check.api_http.4.request_url.1
  - id: svc.assert_check.api_http.5
    config:
      request:
        method: PATCH
        artifact_id: art.svc.assert_check.api_http.5.request_url.1
  - id: svc.assert_check.api_http.6
    config:
      request:
        method: DELETE
        artifact_id: art.svc.assert_check.api_http.6.request_url.1
  - id: svc.assert_check.api_http.7
    config:
      request:
        method: HEAD
        artifact_id: art.svc.assert_check.api_http.7.request_url.1
  - id: svc.assert_check.api_http.8
    config:
      request:
        method: OPTIONS
        artifact_id: art.svc.assert_check.api_http.8.request_url.1
  - id: svc.assert_check.api_http.9
    config:
      request:
        method: TRACE
        artifact_id: art.svc.assert_check.api_http.9.request_url.1
  - id: svc.assert_check.api_http.10
    config:
      request:
        method: GET
        cors:
          preflight: true
          origin: https://client.example
          request_method: POST
        artifact_id: art.svc.assert_check.api_http.10.request_url.1
  - id: svc.assert_check.api_http.11
    config:
      requests:
      - id: create
        method: POST
        artifact_id: art.svc.assert_check.api_http.11.requests_url_1.1
      - id: get
        method: GET
        artifact_id: art.svc.assert_check.api_http.11.requests_url_2.1
      - id: cleanup
        method: DELETE
        artifact_id: art.svc.assert_check.api_http.11.requests_url_3.1
      api_http:
        scenario:
          fail_fast: true
  - id: svc.assert_check.api_http.12
    config:
      request:
        method: GET
        artifact_id: art.svc.assert_check.api_http.12.request_url.1
      api_http:
        mode: deterministic
        auth:
          oauth:
            grant_type: client_credentials
            client_id_env: PATH
            client_secret_env: HOME
            scope: read:spec
            token_asset_id: art.svc.assert_check.api_http.12.oauth_token.1
  - id: svc.assert_check.api_http.13
    config:
      request:
        method: GET
        artifact_id: art.svc.assert_check.api_http.13.request_url.1
      api_http:
        auth:
          oauth:
            grant_type: client_credentials
            client_id_env: SPEC_RUNNER_OAUTH_MISSING_CLIENT_ID
            client_secret_env: SPEC_RUNNER_OAUTH_MISSING_CLIENT_SECRET
            token_asset_id: art.svc.assert_check.api_http.13.oauth_token.1
  - id: svc.assert_check.api_http.14
    config:
      request:
        method: GET
        artifact_id: art.svc.assert_check.api_http.14.request_url.1
      api_http:
        auth:
          oauth:
            grant_type: client_credentials
            client_id_env: PATH
            client_secret_env: HOME
            auth_style: token
            token_asset_id: art.svc.assert_check.api_http.14.oauth_token.1
  - id: svc.assert_check.api_http.15
    config:
      request:
        method: GET
        artifact_id: art.svc.assert_check.api_http.15.request_url.1
      api_http:
        mode: live
        auth:
          oauth:
            grant_type: client_credentials
            client_id_env: OAUTH_CLIENT_ID
            client_secret_env: OAUTH_CLIENT_SECRET
            token_asset_id: art.svc.assert_check.api_http.15.oauth_token.1
  - id: svc.assert_check.api_http.16
    config:
      request:
        method: GET
        artifact_id: art.svc.assert_check.api_http.16.request_url.1
      use:
      - as: lib_http_core_spec
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
        artifact_id: art.svc.assert_check.api_http.16.use_1.1
services:
- id: svc.assert_check.api_http.1
  consumes:
  - svc.assert_check.api_http.1
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.1
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.2
  consumes:
  - svc.assert_check.api_http.2
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.2
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.3
  consumes:
  - svc.assert_check.api_http.3
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.3
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.4
  consumes:
  - svc.assert_check.api_http.4
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.4
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.5
  consumes:
  - svc.assert_check.api_http.5
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.5
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.6
  consumes:
  - svc.assert_check.api_http.6
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.6
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.7
  consumes:
  - svc.assert_check.api_http.7
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.7
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.8
  consumes:
  - svc.assert_check.api_http.8
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.8
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.9
  consumes:
  - svc.assert_check.api_http.9
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.9
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.10
  consumes:
  - svc.assert_check.api_http.10
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.10
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.11
  consumes:
  - svc.assert_check.api_http.11
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.11
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.12
  consumes:
  - svc.assert_check.api_http.12
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.12
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.13
  consumes:
  - svc.assert_check.api_http.13
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.13
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.14
  consumes:
  - svc.assert_check.api_http.14
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.14
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.15
  consumes:
  - svc.assert_check.api_http.15
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.15
      adapter_import: pipe_identity
- id: svc.assert_check.api_http.16
  consumes:
  - svc.assert_check.api_http.16
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.assert_check.api_http.16
      adapter_import: pipe_identity
assets:
- id: art.svc.assert_check.api_http.1.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.3.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_created.json"
- id: art.svc.assert_check.api_http.4.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_item_abc-123.json"
- id: art.svc.assert_check.api_http.5.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_item_abc-123.json"
- id: art.svc.assert_check.api_http.6.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_deleted.json"
- id: art.svc.assert_check.api_http.7.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.8.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.9.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.10.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.11.requests_url_1.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_created.json"
- id: art.svc.assert_check.api_http.11.requests_url_2.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_item_{{steps.create.body_json.id}}.json"
- id: art.svc.assert_check.api_http.11.requests_url_3.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_deleted.json"
- id: art.svc.assert_check.api_http.12.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.12.oauth_token.1
  ref: "/specs/03_conformance/cases/fixtures/oauth_token_ok.json"
- id: art.svc.assert_check.api_http.13.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.13.oauth_token.1
  ref: "/specs/03_conformance/cases/fixtures/oauth_token_ok.json"
- id: art.svc.assert_check.api_http.14.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.14.oauth_token.1
  ref: "/specs/03_conformance/cases/fixtures/oauth_token_ok.json"
- id: art.svc.assert_check.api_http.15.request_url.1
  ref: https://api.example.invalid/items
- id: art.svc.assert_check.api_http.15.oauth_token.1
  ref: https://issuer.example.invalid/oauth/token
- id: art.svc.assert_check.api_http.16.request_url.1
  ref: "/specs/03_conformance/cases/fixtures/api_http_ok.json"
- id: art.svc.assert_check.api_http.16.use_1.1
  ref: "/specs/05_libraries/domain/http_core.spec.md"
artifacts:
- id: body_json
  ref: artifact://api_http/body_json
  type: application/json
- id: body_text
  ref: artifact://api_http/body_text
  type: application/json
- id: context_json
  ref: artifact://api_http/context_json
  type: application/json
- id: status
  ref: artifact://api_http/status
  type: application/json
- id: steps_json
  ref: artifact://api_http/steps_json
  type: application/json
```
