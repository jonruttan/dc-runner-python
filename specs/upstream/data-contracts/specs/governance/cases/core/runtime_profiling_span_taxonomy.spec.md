# Governance Cases

## DCGOV-PROFILE-SPANS-001

```yaml contract-spec
id: DCGOV-PROFILE-SPANS-001
title: run trace records required span taxonomy for timeout diagnosis
purpose: Ensures the canonical run trace includes required run, case, check, and subprocess
  spans used by timeout diagnostics.
type: contract.check
harness:
  root: .
  profiling_span_taxonomy:
    trace_path: specs/governance/cases/fixtures/run_trace_sample.json
    required_spans:
    - run.total
    - runner.dispatch
    - case.run
    - case.chain
    - case.harness
    - check.execute
    - subprocess.exec
    - subprocess.wait
  check:
    profile: governance.scan
    config:
      check: runtime.profiling_span_taxonomy
  use:
  - ref: /specs/libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
```

