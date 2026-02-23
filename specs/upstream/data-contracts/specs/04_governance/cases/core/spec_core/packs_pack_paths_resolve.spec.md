```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PACK-005
    title: pack paths resolve in repository
    purpose: Ensures all pack manifests and referenced case paths exist.
    harness:
      root: "."
      required_paths:
      - "/specs/00_core/packs/runner_contract_pack_v1.yaml"
      - "/specs/00_core/packs/spec_core_maintenance_pack_v1.yaml"
      - "/specs/00_core/packs/project_docs_maintenance_pack_v1.yaml"
      - "/specs/03_conformance/cases/runner_cli/runner_cli_required_help.spec.md"
      - "/specs/03_conformance/cases/runner_cli/runner_cli_required_governance.spec.md"
      - "/specs/03_conformance/cases/runner_cli/runner_cli_required_conformance.spec.md"
      - "/specs/03_conformance/cases/runner_cli/runner_cli_unknown_command.spec.md"
      - "/specs/03_conformance/cases/runner_cli/runner_cli_optional_capability_negotiation.spec.md"
      check:
        profile: governance.scan
        config:
          check: packs.pack_paths_resolve
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
```
