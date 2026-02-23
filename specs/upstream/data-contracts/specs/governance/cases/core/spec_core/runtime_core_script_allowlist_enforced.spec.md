```yaml contract-spec
id: DCGOV-RUNTIME-CORE-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: core script allowlist enforced
purpose: Ensures canonical script allowlist is declared and stable.
type: contract.check
harness:
  root: .
  scripts_manifest:
    path: /specs/01_schema/core_script_allowlist_v1.yaml
    required_tokens:
      - control_plane.sh
      - ci_gate.sh
      - runner_status_ingest.sh
      - runner_bin.sh
      - governance_catalog_validate.sh
      - spec_schema_pin_validate.sh
      - governance_optional_report.sh
      - governance_triage.sh
  check:
    profile: governance.scan
    config:
      check: runtime.core_script_allowlist_enforced
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names: [violation_count]
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
```
