# Runner Job Script Contract Cases

## DCCONF-JOB-004

```yaml contract-spec
id: DCCONF-JOB-004
title: schema registry build via contract.job
purpose: Ensures script command contracts dispatch and return deterministic success state.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: build
      helper: helper.schema.registry_report
      inputs:
        format: json
        out: .artifacts/schema_registry_report.json
        check: false
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-004.fail.json
        format: json
        report_name: DCCONF-JOB-004.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-004.complete.json
        format: json
        report_name: DCCONF-JOB-004.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```

## DCCONF-JOB-005

```yaml contract-spec
id: DCCONF-JOB-005
title: schema registry check via contract.job
purpose: Ensures script command contracts dispatch and return deterministic success state.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: check
      helper: helper.schema.registry_report
      inputs:
        format: json
        out: .artifacts/schema_registry_report.json
        check: true
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-005.fail.json
        format: json
        report_name: DCCONF-JOB-005.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-005.complete.json
        format: json
        report_name: DCCONF-JOB-005.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```

## DCCONF-JOB-006

```yaml contract-spec
id: DCCONF-JOB-006
title: docs lint via contract.job
purpose: Ensures script command contracts dispatch and return deterministic success state.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: lint
      helper: helper.docs.lint
      inputs: {}
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-006.fail.json
        format: json
        report_name: DCCONF-JOB-006.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-006.complete.json
        format: json
        report_name: DCCONF-JOB-006.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```

## DCCONF-JOB-007

```yaml contract-spec
id: DCCONF-JOB-007
title: docs generate build via contract.job
purpose: Ensures script command contracts dispatch and return deterministic success state.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: build
      helper: helper.docs.generate_all
      inputs:
        action: build
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-007.fail.json
        format: json
        report_name: DCCONF-JOB-007.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-007.complete.json
        format: json
        report_name: DCCONF-JOB-007.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```

## DCCONF-JOB-008

```yaml contract-spec
id: DCCONF-JOB-008
title: docs generate check via contract.job
purpose: Ensures script command contracts dispatch and return deterministic success state.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: check
      helper: helper.docs.generate_all
      inputs:
        action: check
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-008.fail.json
        format: json
        report_name: DCCONF-JOB-008.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-008.complete.json
        format: json
        report_name: DCCONF-JOB-008.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```

## DCCONF-JOB-009

```yaml contract-spec
id: DCCONF-JOB-009
title: docs build reference book via contract.job
purpose: Ensures script command contracts dispatch and return deterministic success state.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: build
      helper: helper.docs.generate_all
      inputs:
        action: build
        surface: reference_book
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-009.fail.json
        format: json
        report_name: DCCONF-JOB-009.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-009.complete.json
        format: json
        report_name: DCCONF-JOB-009.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```

## DCCONF-JOB-010

```yaml contract-spec
id: DCCONF-JOB-010
title: docs build check reference book via contract.job
purpose: Ensures script command contracts dispatch and return deterministic success state.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: check
      helper: helper.docs.generate_all
      inputs:
        action: check
        surface: reference_book
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-010.fail.json
        format: json
        report_name: DCCONF-JOB-010.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-010.complete.json
        format: json
        report_name: DCCONF-JOB-010.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```

## DCCONF-JOB-011

```yaml contract-spec
id: DCCONF-JOB-011
title: docs graph export via contract.job
purpose: Ensures script command contracts dispatch and return deterministic success state.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: build
      helper: helper.docs.generate_all
      inputs:
        action: build
        surface: docs_graph
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-011.fail.json
        format: json
        report_name: DCCONF-JOB-011.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-011.complete.json
        format: json
        report_name: DCCONF-JOB-011.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```
