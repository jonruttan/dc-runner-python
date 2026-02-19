# Python Docs Lint Command Cases

## DCIMPL-PY-DOCSLINT-001

```yaml contract-spec
id: DCIMPL-PY-DOCSLINT-001
title: docs_lint_main passes for canonical reference manifest
type: contract.check
harness:
  entrypoint: spec_runner.spec_lang_commands:docs_lint_main
  check:
    profile: cli.run
    config:
      argv: []
      exit_code: 0
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - stdout
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: stdout}
      - 'OK: docs lint passed'
```

## DCIMPL-PY-DOCSLINT-002

```yaml contract-spec
id: DCIMPL-PY-DOCSLINT-002
title: docs_lint_main fails when manifest path is missing
type: contract.check
harness:
  entrypoint: spec_runner.spec_lang_commands:docs_lint_main
  check:
    profile: cli.run
    config:
      argv:
      - --manifest
      - specs/impl/python/fixtures/missing_reference_manifest.yaml
      exit_code: 1
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - stdout
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: stdout}
      - missing reference manifest
```
