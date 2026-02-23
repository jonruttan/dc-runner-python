# Governance Index

Source of truth: spec.governance.index

Executable governance checks for canonical contract enforcement.

## Core Inputs

- Check sets: `/specs/04_governance/check_sets_v1.yaml`
- Check family map: `/specs/04_governance/check_prefix_map_v1.yaml`
- Cases index: `/specs/04_governance/cases/core/index.md`

## Interface Surface

- Runner contact surface: `/specs/governance/`
- Ownership:
  - `/specs/04_governance/**` is canonical and hand-edited.
  - `/specs/governance/**` is generated and committed from canonical files.
  - Refresh with: `./scripts/governance_interface_sync.sh --write`

## Domain Grouping

- Spec-core maintenance: `/specs/04_governance/cases/core/spec_core/`
- Runner-contract maintenance: `/specs/04_governance/cases/core/runner_contract/`
- Project-docs maintenance: `/specs/04_governance/cases/core/project_docs/`

## Subdomains

- Metrics baselines: `/specs/04_governance/metrics/`
- Tool contracts: `/specs/04_governance/tools/`

## Execution

```sh
./scripts/control_plane.sh governance
```

Governance decision logic is sourced from executable spec cases and policy
libraries. Shell scripts in `/scripts/` are transport entrypoints and artifact
emitters only.

## Canonical Checks

- Governance check catalog is generated into `/docs/book/96_appendix_governance_checks_reference.md`.
- Policy and traceability references are generated into `/docs/book/94_appendix_contract_policy_reference.md` and `/docs/book/95_appendix_traceability_reference.md`.
