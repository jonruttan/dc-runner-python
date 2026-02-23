# Conformance Index

Source of truth: spec.conformance.index

Cross-runner conformance fixtures and report contracts.

## Canonical Inputs

- Style contract: `/specs/03_conformance/style.md`
- Report format: `/specs/03_conformance/report_format.md`
- Purpose lint policy: `/specs/03_conformance/purpose_lint_v1.yaml`
- Cases index: `/specs/03_conformance/cases/index.md`

## Execution

```sh
./scripts/runner_bin.sh conformance-parity --cases specs/03_conformance/cases --out .artifacts/conformance-parity.json
```

## Related Generated References

- `/docs/book/97_appendix_metrics_reference.md`
