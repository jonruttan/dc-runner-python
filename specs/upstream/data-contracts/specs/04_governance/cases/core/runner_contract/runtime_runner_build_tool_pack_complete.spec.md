```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    pack:
      path: /specs/00_core/packs/runner_contract_pack_v1.yaml
      required_tokens:
      - /specs/02_contracts/30_build_tool_command_set.md
      - /specs/02_contracts/33_bundle_package_management.md
      - /specs/02_contracts/34_runner_implementation_spec_bundles.md
      - /specs/01_schema/runner_build_tool_contract_v1.yaml
      - /specs/01_schema/project_bundle_lock_v1.yaml
      - /specs/01_schema/bundle_manifest_v1.yaml
      - /specs/01_schema/resolved_bundle_lock_v1.yaml
      - /specs/01_schema/implementation_bundle_overlay_v1.yaml
      - /specs/01_schema/implementation_bundle_build_lock_v1.yaml
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_required_core.spec.md
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_required_sync.spec.md
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_bundle_lock_schema.spec.md
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_bundle_asset_naming.spec.md
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_impl_overlay_schema.spec.md
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_impl_bundle_commands.spec.md
      - /specs/03_conformance/cases/runner_build_tool/runner_build_tool_project_lock_additional_role.spec.md
    check:
      profile: governance.scan
      config:
        check: packs.runner_contract_pack_complete
contracts:
  clauses:
  - id: DCGOV-RUNTIME-BTOOL-003
    title: runner contract pack includes build tool contract surface
    purpose: Ensures runner contract pack includes build tool contract and conformance
      case coverage.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        required: false
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
  - id: act.gov.runtime.runner.build.too.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.runner.build.too.1
  consumes:
  - act.gov.runtime.runner.build.too.1
```
