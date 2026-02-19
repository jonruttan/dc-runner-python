# Domain Library Conformance Cases

## DCCONF-DOMAIN-LIB-001

```yaml contract-spec
id: DCCONF-DOMAIN-LIB-001
title: domain http library defines status helper
purpose: Ensures domain HTTP library exports reusable status-based assertion helper.
type: contract.check
harness:
  check:
    profile: text.file
    config:
      path: /specs/libraries/domain/http_core.spec.md
  use:
  - ref: /specs/libraries/domain/http_core.spec.md
    as: lib_http_core_spec
    symbols:
    - domain.http.auth_is_oauth
    - domain.http.body_json
    - domain.http.body_json_has_key
    - domain.http.body_json_type_is
    - domain.http.body_text
    - domain.http.has_bearer_header
    - domain.http.header_contains
    - domain.http.header_get
    - domain.http.oauth_scope_requested
    - domain.http.oauth_token_source_is
    - domain.http.ok_2xx
    - domain.http.status
    - domain.http.status_in
    - domain.http.status_is
    - domain.http.status_is_forbidden
    - domain.http.status_is_unauthorized
expect:
  portable:
    status: pass
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
    - std.logic.eq:
      - call:
        - {var: domain.http.status}
        - lit:
            value:
              status: 200
              headers:
                Authorization: Bearer abc
                content-type: application/json
              body_text: ok
              body_json:
                ok: true
            meta:
              auth_mode: oauth
            context:
              oauth:
                scope_requested: read:items
      - 200
    - call:
      - {var: domain.http.status_is}
      - lit:
          value:
            status: 200
          meta: {}
      - 200
    - call:
      - {var: domain.http.status_is_unauthorized}
      - lit:
          value:
            status: 401
          meta: {}
    - call:
      - {var: domain.http.status_is_forbidden}
      - lit:
          value:
            status: 403
          meta: {}
    - call:
      - {var: domain.http.ok_2xx}
      - lit:
          value:
            status: 204
          meta: {}
    - call:
      - {var: domain.http.status_in}
      - lit:
          value:
            status: 200
            headers:
              Authorization: Bearer abc
              content-type: application/json
            body_text: ok
            body_json:
              ok: true
          meta:
            auth_mode: oauth
          context:
            oauth:
              scope_requested: read:items
      - lit:
        - 200
        - 201
    - std.logic.eq:
      - call:
        - {var: domain.http.header_get}
        - lit:
            value:
              headers:
                Authorization: Bearer abc
            meta: {}
        - Authorization
      - Bearer abc
    - call:
      - {var: domain.http.header_contains}
      - lit:
          value:
            headers:
              Authorization: Bearer abc
          meta: {}
      - Authorization
      - Bearer
    - std.logic.eq:
      - call:
        - {var: domain.http.body_text}
        - lit:
            value:
              body_text: ok
            meta: {}
      - ok
    - call:
      - {var: domain.http.body_json}
      - lit:
          value:
            body_json:
              ok: true
          meta: {}
    - call:
      - {var: domain.http.body_json_type_is}
      - lit:
          value:
            body_json:
              ok: true
          meta: {}
      - object
    - call:
      - {var: domain.http.body_json_has_key}
      - lit:
          value:
            body_json:
              ok: true
          meta: {}
      - ok
    - call:
      - {var: domain.http.auth_is_oauth}
      - lit:
          value: {}
          meta:
            auth_mode: oauth
    - call:
      - {var: domain.http.has_bearer_header}
      - lit:
          value:
            headers:
              Authorization: Bearer abc
          meta: {}
    - call:
      - {var: domain.http.oauth_scope_requested}
      - lit:
          value: {}
          meta: {}
          context:
            oauth:
              scope_requested: read:items
    - call:
      - {var: domain.http.oauth_token_source_is}
      - lit:
          value: {}
          meta:
            oauth_token_source: env_ref
      - env_ref
    - std.string.contains:
      - {var: text}
      - domain.http.status_in
    - std.string.contains:
      - {var: text}
      - domain.http.auth_is_oauth
    - std.string.contains:
      - {var: text}
      - 'type: spec.export'
```

## DCCONF-DOMAIN-LIB-002

```yaml contract-spec
id: DCCONF-DOMAIN-LIB-002
title: domain library index references all domain library files
purpose: Ensures domain index remains synchronized with all domain library spec files.
type: contract.check
harness:
  check:
    profile: text.file
    config:
      path: /specs/libraries/domain/index.md
  use:
  - ref: /specs/libraries/domain/make_core.spec.md
    as: lib_make_core_spec
    symbols:
    - make.has_target
  - ref: /specs/libraries/domain/markdown_core.spec.md
    as: lib_markdown_core_spec
    symbols:
    - domain.markdown.code_fence_language_exists
    - domain.markdown.has_broken_links
    - domain.markdown.has_heading
    - domain.markdown.has_yaml_spec_test_fence
    - domain.markdown.heading_level_exists
    - domain.markdown.link_targets_all_resolve
    - domain.markdown.required_sections_present
    - domain.markdown.section_order_valid
    - domain.markdown.token_dependencies_resolved
    - domain.markdown.token_ownership_unique
    - domain.markdown.token_present
    - domain.markdown.tokens_all_present
  - ref: /specs/libraries/domain/fs_core.spec.md
    as: lib_fs_core_spec
    symbols:
    - domain.fs.file_ext_eq
    - domain.fs.glob_all
    - domain.fs.glob_any_spec_files
    - domain.fs.glob_filter
    - domain.fs.is_docs_spec_file
    - domain.fs.json_get_text
    - domain.fs.json_get_or_text
    - domain.fs.json_has_path_text
    - domain.fs.json_path_eq_text
    - domain.fs.sort_spec_files
  - ref: /specs/libraries/domain/path_core.spec.md
    as: lib_path_core_spec
    symbols:
    - domain.path.normalize
    - domain.path.eq
    - domain.path.is_spec_md
    - domain.path.is_in_docs
    - domain.path.sorted
    - domain.file.is_existing_file
    - domain.file.is_existing_dir
    - domain.file.has_ext
    - domain.file.name
  - ref: /specs/libraries/domain/python_core.spec.md
    as: lib_python_core_spec
    symbols:
    - py.is_tuple_projection
  - ref: /specs/libraries/domain/php_core.spec.md
    as: lib_php_core_spec
    symbols:
    - php.is_assoc_projection
expect:
  portable:
    status: pass
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
    - call:
      - {var: make.has_target}
      - lit:
          value: "ci-gate:\n\t@echo ok\n"
          meta: {}
      - ci-gate
    - call:
      - {var: py.is_tuple_projection}
      - lit:
          value:
          - 1
          - 2
          meta:
            native_kind: python.tuple
    - call:
      - {var: php.is_assoc_projection}
      - lit:
          value:
            k: v
          meta:
            php_array_kind: assoc
    - std.logic.eq:
      - call:
        - {var: domain.path.normalize}
        - /docs//spec/./libraries/domain/http_core.spec.md
      - /specs/libraries/domain/http_core.spec.md
    - call:
      - {var: domain.path.eq}
      - /specs/libraries/domain/http_core.spec.md
      - /specs/libraries/domain//http_core.spec.md
    - call:
      - {var: domain.path.is_spec_md}
      - /specs/libraries/domain/http_core.spec.md
    - call:
      - {var: domain.path.is_in_docs}
      - /specs/libraries/domain/http_core.spec.md
    - std.logic.eq:
      - call:
        - {var: domain.path.sorted}
        - lit:
          - /docs/b
          - /docs/a
      - lit:
        - /docs/a
        - /docs/b
    - call:
      - {var: domain.fs.is_docs_spec_file}
      - /specs/conformance/cases/core/domain_libraries.spec.md
    - std.logic.eq:
      - call:
        - {var: domain.fs.sort_spec_files}
        - lit:
          - /docs/b.md
          - /docs/a.spec.md
          - /docs/a.md
          - /docs/b.spec.md
      - lit:
        - /docs/a.spec.md
        - /docs/b.spec.md
    - call:
      - {var: domain.fs.glob_any_spec_files}
      - lit:
        - /docs/a.md
        - /docs/a.spec.md
    - std.logic.eq:
      - call:
        - {var: domain.fs.glob_filter}
        - lit:
          - /docs/a.md
          - /docs/a.spec.md
          - /docs/b.spec.md
        - '*.spec.md'
      - lit:
        - /docs/a.spec.md
        - /docs/b.spec.md
    - call:
      - {var: domain.fs.glob_all}
      - lit:
        - /docs/a.spec.md
        - /docs/b.spec.md
      - '*.spec.md'
    - std.logic.eq:
      - call:
        - {var: domain.fs.json_get_text}
        - '{"a":{"b":7}}'
        - lit:
          - a
          - b
      - 7
    - std.logic.eq:
      - call:
        - {var: domain.fs.json_get_or_text}
        - '{"a":{"b":7}}'
        - lit:
          - a
          - b
        - 0
      - 7
    - call:
      - {var: domain.fs.json_has_path_text}
      - '{"a":{"b":7}}'
      - lit:
        - a
        - b
    - call:
      - {var: domain.fs.json_path_eq_text}
      - '{"a":{"b":7}}'
      - lit:
        - a
        - b
      - 7
    - call:
      - {var: domain.fs.file_ext_eq}
      - lit:
          path: /specs/libraries/domain/http_core.spec.md
      - md
    - call:
      - {var: domain.file.is_existing_file}
      - lit:
          path: /specs/libraries/domain/http_core.spec.md
          exists: true
          type: file
    - call:
      - {var: domain.file.is_existing_dir}
      - lit:
          path: /specs/libraries/domain
          exists: true
          type: dir
    - call:
      - {var: domain.file.has_ext}
      - lit:
          path: /specs/libraries/domain/http_core.spec.md
      - .md
    - std.logic.eq:
      - call:
        - {var: domain.file.name}
        - lit:
            path: /specs/libraries/domain/http_core.spec.md
      - http_core.spec.md
    - std.string.contains:
      - {var: text}
      - /specs/libraries/domain/http_core.spec.md
    - std.string.contains:
      - {var: text}
      - /specs/libraries/domain/fs_core.spec.md
    - std.string.contains:
      - {var: text}
      - /specs/libraries/domain/make_core.spec.md
    - std.string.contains:
      - {var: text}
      - /specs/libraries/domain/markdown_core.spec.md
    - std.string.contains:
      - {var: text}
      - /specs/libraries/domain/path_core.spec.md
    - std.string.contains:
      - {var: text}
      - /specs/libraries/domain/php_core.spec.md
    - std.string.contains:
      - {var: text}
      - /specs/libraries/domain/python_core.spec.md
```
