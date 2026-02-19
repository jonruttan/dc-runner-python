# Python Script CLI Cases: Docs Generate and Style

## DCIMPL-PY-SCRIPT-DOCS-001

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-DOCS-001
title: docs_generate_all help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:docs_generate_all_main
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
      - --surface
```

## DCIMPL-PY-SCRIPT-DOCS-002

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-DOCS-002
title: docs_generate_all fails on unknown surface
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:docs_generate_all_main
  check:
    profile: cli.run
    config:
      argv:
      - --check
      - --surface
      - nope
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
      std.logic.eq:
      - 1
      - 1
```

## DCIMPL-PY-SCRIPT-DOCS-003

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-DOCS-003
title: docs_generate_specs help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:docs_generate_specs_main
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

## DCIMPL-PY-SCRIPT-DOCS-004

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-DOCS-004
title: docs_generate_specs fails on unknown surface
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:docs_generate_specs_main
  check:
    profile: cli.run
    config:
      argv:
      - --check
      - --surface
      - nope
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
      - unknown surface_id
```

## DCIMPL-PY-SCRIPT-DOCS-005

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-DOCS-005
title: evaluate_style help renders usage
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:evaluate_style_main
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

## DCIMPL-PY-SCRIPT-DOCS-006

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-DOCS-006
title: evaluate_style check defaults to docs spec tree
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:evaluate_style_main
  check:
    profile: cli.run
    config:
      argv:
      - --check
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
      - formatting is canonical
```

## DCIMPL-PY-SCRIPT-DOCS-007

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-DOCS-007
title: docs_build_reference writes artifacts to explicit outputs
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:docs_build_reference_main
  check:
    profile: cli.run
    config:
      argv:
      - --manifest
      - docs/book/reference_manifest.yaml
      - --index-out
      - .artifacts/docs-build-reference-index.md
      - --coverage-out
      - .artifacts/docs-build-reference-coverage.md
      - --graph-out
      - .artifacts/docs-build-reference-graph.json
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
    - std.string.contains:
      - {var: stdout}
      - wrote .artifacts/docs-build-reference-index.md
    - std.string.contains:
      - {var: stdout}
      - wrote .artifacts/docs-build-reference-coverage.md
    - std.string.contains:
      - {var: stdout}
      - wrote .artifacts/docs-build-reference-graph.json
```

## DCIMPL-PY-SCRIPT-DOCS-008

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-DOCS-008
title: docs_build_reference rejects unknown args
type: contract.check
harness:
  entrypoint: spec_runner.script_entrypoints:docs_build_reference_main
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
