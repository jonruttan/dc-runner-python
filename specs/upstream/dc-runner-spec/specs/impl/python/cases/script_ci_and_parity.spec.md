# Python Script CLI Cases: CI and Parity

## DCIMPL-PY-SCRIPT-CI-001

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-001
title: ci_gate_summary command help renders usage
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:ci_gate_summary_main
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
      - --runner-bin
```

## DCIMPL-PY-SCRIPT-CI-002

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-002
title: ci_gate_summary requires runner-bin
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:ci_gate_summary_main
  check:
    profile: cli.run
    config:
      argv: []
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
      - --runner-bin
```

## DCIMPL-PY-SCRIPT-CI-003

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-003
title: compare_conformance_parity command help renders usage
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:compare_conformance_parity_main
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
      - --cases
```

## DCIMPL-PY-SCRIPT-CI-004

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-004
title: compare_conformance_parity rejects invalid timeout arg
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:compare_conformance_parity_main
  check:
    profile: cli.run
    config:
      argv:
      - --python-timeout-seconds
      - x
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
      - invalid int value
```

## DCIMPL-PY-SCRIPT-CI-005

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-005
title: python conformance runner help renders required flags
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:python_conformance_runner_main
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
    - call:
      - {var: policy.text.contains_pair}
      - {var: stdout}
      - --cases
      - --out
    - std.string.contains:
      - {var: stdout}
      - --case-file-pattern
```

## DCIMPL-PY-SCRIPT-CI-006

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-006
title: python conformance runner rejects empty case pattern
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:python_conformance_runner_main
  check:
    profile: cli.run
    config:
      argv:
      - --cases
      - specs/conformance/cases
      - --out
      - .artifacts/python-conformance-script-case.json
      - --case-file-pattern
      - ''
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
      - case-file-pattern
```

## DCIMPL-PY-SCRIPT-CI-007

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-007
title: php conformance runner usage includes required flags
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  check:
    profile: text.file
    config:
      path: /dc-runner-php
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
      - {var: policy.text.contains_pair}
      - {var: text}
      - --cases <dir-or-file>
      - --out <file>
    - std.string.contains:
      - {var: text}
      - --case-file-pattern <glob>
```

## DCIMPL-PY-SCRIPT-CI-008

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-008
title: compare_conformance_parity rejects empty case formats
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:compare_conformance_parity_main
  check:
    profile: cli.run
    config:
      argv:
      - --case-formats
      - ''
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
      - --case-formats requires at least one format
```

## DCIMPL-PY-SCRIPT-CI-009

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CI-009
title: compare_conformance_parity reports missing php executable
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.script_entrypoints:compare_conformance_parity_main
  env:
    PATH: /nonexistent
  check:
    profile: cli.run
    config:
      argv:
      - --cases
      - specs/conformance/cases
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
      - php executable not found in PATH
```
