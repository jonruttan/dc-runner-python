# Conformance Index

Source of truth: spec.conformance.index

Cross-runner conformance fixtures and report contracts.

## Canonical Inputs

- Style contract: `/specs/conformance/style.md`
- Report format: `/specs/conformance/report_format.md`
- Purpose lint policy: `/specs/conformance/purpose_lint_v1.yaml`
- Cases index: `/specs/conformance/cases/index.md`

## Execution

```sh
./runners/public/runner_adapter.sh --impl rust conformance-parity --cases specs/conformance/cases --out .artifacts/conformance-parity.json
```

## Related Generated References

- `/docs/book/97_appendix_metrics_reference.md`
