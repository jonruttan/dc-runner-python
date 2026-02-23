```yaml contract-spec
id: DCIMPL-PY-DOCSLINT-001
title: docs_lint_main passes for canonical reference manifest
type: contract.check
harness:
  use:
  - ref: /specs/05_libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
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


```yaml contract-spec
id: DCIMPL-PY-DOCSLINT-002
title: docs_lint_main fails when manifest path is missing
type: contract.check
harness:
  use:
  - ref: /specs/05_libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.spec_lang_commands:docs_lint_main
  check:
    profile: cli.run
    config:
      argv:
      - --manifest
      - specs/impl/python/cases/fixtures/missing_reference_manifest.yaml
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
