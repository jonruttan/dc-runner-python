```yaml contract-spec
id: DCCONF-JOB-REP-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: conformance purpose json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: conformance-purpose
        format: json
        out: .artifacts/conformance-purpose.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-001.fail.json
        format: json
        report_name: DCCONF-JOB-REP-001.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-001.complete.json
        format: json
        report_name: DCCONF-JOB-REP-001.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/conformance-purpose.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: conformance purpose markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: conformance-purpose
        format: md
        out: .artifacts/conformance-purpose-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-002.fail.json
        format: json
        report_name: DCCONF-JOB-REP-002.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-002.complete.json
        format: json
        report_name: DCCONF-JOB-REP-002.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/conformance-purpose-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec portability json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: spec-portability
        format: json
        out: .artifacts/spec-portability.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-003.fail.json
        format: json
        report_name: DCCONF-JOB-REP-003.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-003.complete.json
        format: json
        report_name: DCCONF-JOB-REP-003.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/spec-portability.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec portability markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: spec-portability
        format: md
        out: .artifacts/spec-portability-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-004.fail.json
        format: json
        report_name: DCCONF-JOB-REP-004.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-004.complete.json
        format: json
        report_name: DCCONF-JOB-REP-004.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/spec-portability-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: contract assertions json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: contract-assertions
        format: json
        out: .artifacts/contract-assertions.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-005.fail.json
        format: json
        report_name: DCCONF-JOB-REP-005.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-005.complete.json
        format: json
        report_name: DCCONF-JOB-REP-005.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/contract-assertions.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-006
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: contract assertions markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: contract-assertions
        format: md
        out: .artifacts/contract-assertions-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-006.fail.json
        format: json
        report_name: DCCONF-JOB-REP-006.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-006.complete.json
        format: json
        report_name: DCCONF-JOB-REP-006.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/contract-assertions-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-007
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec lang adoption json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: spec-lang-adoption
        format: json
        out: .artifacts/spec-lang-adoption.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-007.fail.json
        format: json
        report_name: DCCONF-JOB-REP-007.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-007.complete.json
        format: json
        report_name: DCCONF-JOB-REP-007.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/spec-lang-adoption.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-008
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec lang adoption markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: spec-lang-adoption
        format: md
        out: .artifacts/spec-lang-adoption-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-008.fail.json
        format: json
        report_name: DCCONF-JOB-REP-008.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-008.complete.json
        format: json
        report_name: DCCONF-JOB-REP-008.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/spec-lang-adoption-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-009
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner independence json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: runner-independence
        format: json
        out: .artifacts/runner-independence.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-009.fail.json
        format: json
        report_name: DCCONF-JOB-REP-009.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-009.complete.json
        format: json
        report_name: DCCONF-JOB-REP-009.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/runner-independence.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-010
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner independence markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: runner-independence
        format: md
        out: .artifacts/runner-independence-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-010.fail.json
        format: json
        report_name: DCCONF-JOB-REP-010.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-010.complete.json
        format: json
        report_name: DCCONF-JOB-REP-010.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/runner-independence-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-011
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: python dependency json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: python-dependency
        format: json
        out: .artifacts/python-dependency.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-011.fail.json
        format: json
        report_name: DCCONF-JOB-REP-011.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-011.complete.json
        format: json
        report_name: DCCONF-JOB-REP-011.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/python-dependency.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-012
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: python dependency markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: python-dependency
        format: md
        out: .artifacts/python-dependency-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-012.fail.json
        format: json
        report_name: DCCONF-JOB-REP-012.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-012.complete.json
        format: json
        report_name: DCCONF-JOB-REP-012.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/python-dependency-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-013
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: docs operability json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: docs-operability
        format: json
        out: .artifacts/docs-operability.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-013.fail.json
        format: json
        report_name: DCCONF-JOB-REP-013.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-013.complete.json
        format: json
        report_name: DCCONF-JOB-REP-013.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/docs-operability.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-014
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: docs operability markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: docs-operability
        format: md
        out: .artifacts/docs-operability-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-014.fail.json
        format: json
        report_name: DCCONF-JOB-REP-014.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-014.complete.json
        format: json
        report_name: DCCONF-JOB-REP-014.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/docs-operability-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-015
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: objective scorecard json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: objective-scorecard
        format: json
        out: .artifacts/objective-scorecard.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-015.fail.json
        format: json
        report_name: DCCONF-JOB-REP-015.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-015.complete.json
        format: json
        report_name: DCCONF-JOB-REP-015.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/objective-scorecard.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-016
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: objective scorecard markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: objective-scorecard
        format: md
        out: .artifacts/objective-scorecard-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-016.fail.json
        format: json
        report_name: DCCONF-JOB-REP-016.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-016.complete.json
        format: json
        report_name: DCCONF-JOB-REP-016.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/objective-scorecard-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-017
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec lang stdlib json report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: spec-lang-stdlib
        format: json
        out: .artifacts/spec-lang-stdlib.json
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-017.fail.json
        format: json
        report_name: DCCONF-JOB-REP-017.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-017.complete.json
        format: json
        report_name: DCCONF-JOB-REP-017.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/spec-lang-stdlib.json
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```


```yaml contract-spec
id: DCCONF-JOB-REP-018
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec lang stdlib markdown report
purpose: Ensures report contract jobs dispatch and write the expected artifact output path.
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: report
      helper: helper.report.emit
      inputs:
        report_name: spec-lang-stdlib
        format: md
        out: .artifacts/spec-lang-stdlib-summary.md
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-018.fail.json
        format: json
        report_name: DCCONF-JOB-REP-018.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCCONF-JOB-REP-018.complete.json
        format: json
        report_name: DCCONF-JOB-REP-018.complete
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
    - std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - .artifacts/spec-lang-stdlib-summary.md
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```
