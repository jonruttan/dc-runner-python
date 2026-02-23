```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    taxonomy_layout:
      required_paths:
      - /specs/04_governance/metrics
      - /specs/04_governance/tools
      - /specs/04_governance
      - /specs/00_core/current.md
      - /specs/01_schema/index.md
      - /specs/02_contracts/index.md
      forbidden_paths:
      - /specs/metrics
      - /specs/tools
      - /specs/pending
      - /specs/schema.md
      - /specs/portable_contract.md
    check:
      profile: governance.scan
      config:
        check: spec.taxonomy_hard_cut_required
    use:
    - ref: /specs/05_libraries/policy/policy_assertions.spec.md
      as: lib_policy_core_spec
      symbols:
      - policy.assert.no_violations
      - policy.assert.summary_passed
      - policy.assert.summary_check_id
      - policy.assert.scan_pass
contracts:
  clauses:
  - id: DCGOV-SPEC-TOPO-001
    title: specs taxonomy hard-cut layout is canonical
    purpose: Ensures governance utility domains are folded under `/specs/04_governance/*`
      and canonical root shim paths are removed.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.spec.taxonomy.hard.cut.r.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.spec.taxonomy.hard.cut.r.1
  consumes:
  - act.gov.spec.taxonomy.hard.cut.r.1
```
