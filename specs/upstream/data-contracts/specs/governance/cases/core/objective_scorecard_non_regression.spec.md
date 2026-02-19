# Governance Cases

## DCGOV-OBJECTIVE-002

```yaml contract-spec
id: DCGOV-OBJECTIVE-002
title: objective scorecard is non-regressing
purpose: Enforces ratchet non-regression for objective scorecard summary metrics and baseline-note
  integrity.
type: contract.check
harness:
  root: .
  objective_scorecard_non_regression:
    baseline_path: /specs/governance/metrics/objective_scorecard_baseline.json
    summary_fields:
      overall_min_score: non_decrease
      overall_mean_score: non_decrease
      tripwire_hit_count: non_increase
    epsilon: 1.0e-12
    objective_scorecard:
      manifest_path: /specs/governance/metrics/objective_manifest.yaml
    baseline_notes:
      path: /specs/governance/metrics/baseline_update_notes.yaml
      baseline_paths:
      - /specs/governance/metrics/spec_portability_baseline.json
      - /specs/governance/metrics/spec_lang_adoption_baseline.json
      - /specs/governance/metrics/runner_independence_baseline.json
      - /specs/governance/metrics/docs_operability_baseline.json
      - /specs/governance/metrics/contract_assertions_baseline.json
      - /specs/governance/metrics/objective_scorecard_baseline.json
  check:
    profile: governance.scan
    config:
      check: objective.scorecard_non_regression
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
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - objective.scorecard_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
