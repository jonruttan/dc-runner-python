# Python Script CLI Cases: Portability and Migration

## DCIMPL-PY-SCRIPT-PORT-001

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-PORT-001
title: spec_portability_report writes json artifact
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:spec_portability_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --out
      - .artifacts/spec-portability-script-case.json
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
      - wrote .artifacts/spec-portability-script-case.json
```

## DCIMPL-PY-SCRIPT-PORT-002

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-PORT-002
title: spec_portability_report rejects invalid format
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:spec_portability_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --format
      - nope
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

## DCIMPL-PY-SCRIPT-PORT-003

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-PORT-003
title: impl evaluate migration report help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:impl_evaluate_migration_report_main
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

## DCIMPL-PY-SCRIPT-PORT-004

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-PORT-004
title: impl evaluate migration report rejects invalid option
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:impl_evaluate_migration_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --unknown-option
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
      - unrecognized arguments
```

## DCIMPL-PY-SCRIPT-PORT-005

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-PORT-005
title: split library cases command help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:split_library_cases_per_symbol_main
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
      - --write
```

## DCIMPL-PY-SCRIPT-PORT-006

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-PORT-006
title: split library cases command requires input paths
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:split_library_cases_per_symbol_main
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
      - paths
```

## DCIMPL-PY-SCRIPT-PORT-007

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-PORT-007
title: conformance purpose report writes json artifact
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:conformance_purpose_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --out
      - .artifacts/conformance-purpose-script-case.json
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
      - wrote .artifacts/conformance-purpose-script-case.json
```

## DCIMPL-PY-SCRIPT-PORT-008

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-PORT-008
title: conformance purpose report rejects invalid format
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:conformance_purpose_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --format
      - nope
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
