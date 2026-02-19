# Python Script CLI Cases: Catalog Generators

## DCIMPL-PY-SCRIPT-CATALOG-001

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-001
title: generate governance check catalog help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_governance_check_catalog_main
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
      - --doc-out
```

## DCIMPL-PY-SCRIPT-CATALOG-002

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-002
title: generate governance check catalog rejects unknown arg
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_governance_check_catalog_main
  check:
    profile: cli.run
    config:
      argv:
      - --bad-flag
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

## DCIMPL-PY-SCRIPT-CATALOG-003

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-003
title: generate harness type catalog help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_harness_type_catalog_main
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
      - --doc-out
```

## DCIMPL-PY-SCRIPT-CATALOG-004

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-004
title: generate harness type catalog rejects unknown arg
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_harness_type_catalog_main
  check:
    profile: cli.run
    config:
      argv:
      - --bad-flag
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

## DCIMPL-PY-SCRIPT-CATALOG-005

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-005
title: generate metrics field catalog help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_metrics_field_catalog_main
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
      - --doc-out
```

## DCIMPL-PY-SCRIPT-CATALOG-006

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-006
title: generate metrics field catalog rejects unknown arg
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_metrics_field_catalog_main
  check:
    profile: cli.run
    config:
      argv:
      - --bad-flag
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

## DCIMPL-PY-SCRIPT-CATALOG-007

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-007
title: generate policy rule catalog help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_policy_rule_catalog_main
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
      - --doc-out
```

## DCIMPL-PY-SCRIPT-CATALOG-008

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-008
title: generate policy rule catalog rejects unknown arg
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_policy_rule_catalog_main
  check:
    profile: cli.run
    config:
      argv:
      - --bad-flag
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

## DCIMPL-PY-SCRIPT-CATALOG-009

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-009
title: generate runner api catalog help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_runner_api_catalog_main
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
      - --doc-out
```

## DCIMPL-PY-SCRIPT-CATALOG-010

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-010
title: generate runner api catalog rejects unknown arg
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_runner_api_catalog_main
  check:
    profile: cli.run
    config:
      argv:
      - --bad-flag
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

## DCIMPL-PY-SCRIPT-CATALOG-011

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-011
title: generate spec lang builtin catalog help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_spec_lang_builtin_catalog_main
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
      - --doc-out
```

## DCIMPL-PY-SCRIPT-CATALOG-012

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-012
title: generate spec lang builtin catalog rejects unknown arg
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_spec_lang_builtin_catalog_main
  check:
    profile: cli.run
    config:
      argv:
      - --bad-flag
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

## DCIMPL-PY-SCRIPT-CATALOG-013

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-013
title: generate spec schema field catalog help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_spec_schema_field_catalog_main
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
      - --schema-doc-out
```

## DCIMPL-PY-SCRIPT-CATALOG-014

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-014
title: generate spec schema field catalog rejects unknown arg
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_spec_schema_field_catalog_main
  check:
    profile: cli.run
    config:
      argv:
      - --bad-flag
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

## DCIMPL-PY-SCRIPT-CATALOG-015

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-015
title: generate traceability catalog help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_traceability_catalog_main
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
      - --doc-out
```

## DCIMPL-PY-SCRIPT-CATALOG-016

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-CATALOG-016
title: generate traceability catalog rejects unknown arg
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:generate_traceability_catalog_main
  check:
    profile: cli.run
    config:
      argv:
      - --bad-flag
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
