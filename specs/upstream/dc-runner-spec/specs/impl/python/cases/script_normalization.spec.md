```yaml contract-spec
id: DCIMPL-PY-SCRIPT-NORM-001
title: normalize_docs_layout help renders usage
type: contract.check
harness:
  use:
  - ref: /specs/05_libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:normalize_docs_layout_main
  check:
    profile: cli.run
    config:
      argv:
      - --help
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
      - --profile
```


```yaml contract-spec
id: DCIMPL-PY-SCRIPT-NORM-002
title: normalize_docs_layout rejects conflicting modes
type: contract.check
harness:
  use:
  - ref: /specs/05_libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:normalize_docs_layout_main
  check:
    profile: cli.run
    config:
      argv:
      - --check
      - --write
      exit_code: 2
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - stderr
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: stderr}
      - not allowed with argument
```


```yaml contract-spec
id: DCIMPL-PY-SCRIPT-NORM-003
title: normalize_repo help renders usage
type: contract.check
harness:
  use:
  - ref: /specs/05_libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:normalize_repo_main
  check:
    profile: cli.run
    config:
      argv:
      - --help
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
      - --scope
```


```yaml contract-spec
id: DCIMPL-PY-SCRIPT-NORM-004
title: normalize_repo rejects invalid scope
type: contract.check
harness:
  use:
  - ref: /specs/05_libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:normalize_repo_main
  check:
    profile: cli.run
    config:
      argv:
      - --check
      - --scope
      - bad
      exit_code: 2
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - stderr
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: stderr}
      - invalid choice
```
