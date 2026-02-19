# Governance Index

Source of truth: spec.governance.index

Executable governance checks for canonical contract enforcement.

## Core Inputs

- Check sets: `/specs/governance/check_sets_v1.yaml`
- Check family map: `/specs/governance/check_catalog_map_v1.yaml`
- Cases index: `/specs/governance/cases/core/index.md`

## Subdomains

- Metrics baselines: `/specs/governance/metrics/`
- Tool contracts: `/specs/governance/tools/`
- Pending governance work: `/specs/governance/pending/`

## Execution

```sh
./runners/public/runner_adapter.sh --impl rust governance
```

## Canonical Checks

- Governance check catalog is generated into `/docs/book/96_appendix_governance_checks_reference.md`.
- Policy and traceability references are generated into `/docs/book/94_appendix_contract_policy_reference.md` and `/docs/book/95_appendix_traceability_reference.md`.
