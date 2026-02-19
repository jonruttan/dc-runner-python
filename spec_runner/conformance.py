from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from spec_runner.codecs import load_external_cases
from spec_runner.dispatcher import SpecRunContext, run_case
from spec_runner.doc_parser import SpecDocTest


@dataclass(frozen=True)
class ConformanceResult:
    id: str
    status: str
    category: str | None
    message: str | None = None


@dataclass(frozen=True)
class ExpectedConformanceResult:
    id: str
    status: str
    category: str | None
    message_tokens: list[str] | None = None


_VALID_STATUS = {"pass", "fail", "skip"}
_VALID_CATEGORY = {"schema", "assertion", "runtime"}
_DEFAULT_CAPABILITIES: dict[str, set[str]] = {
    "python": {
        "api.http",
        "cli.run",
        "assert.op.evaluate",
        "evaluate.spec_lang.v1",
        "evaluate.spec_lang.ramda.v1",
        "evaluate.spec_lang.ramda.v1",
        "assert.group.must",
        "assert.group.may",
        "assert.group.must_not",
        "assert_health.ah001",
        "assert_health.ah002",
        "assert_health.ah003",
        "assert_health.ah004",
        "assert_health.ah005",
        "requires.capabilities",
    },
    "php": {
        "api.http",
        "assert.op.evaluate",
        "evaluate.spec_lang.v1",
        "assert.group.must",
        "assert.group.may",
        "assert.group.must_not",
        "assert_health.ah005",
        "requires.capabilities",
    },
}


def default_capabilities_for(implementation: str) -> set[str]:
    impl = str(implementation).strip() or "python"
    return set(_DEFAULT_CAPABILITIES.get(impl, set()))


def _read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_conformance_cases(
    cases_dir: Path,
    *,
    case_file_pattern: str | None = None,
    case_formats: set[str] | None = None,
) -> list[tuple[Path, dict[str, Any]]]:
    out: list[tuple[Path, dict[str, Any]]] = []
    for doc_path, test in load_external_cases(
        cases_dir,
        formats=case_formats or {"md"},
        md_pattern=case_file_pattern,
    ):
        out.append((doc_path, dict(test)))
    return out


def _parse_expected_entry(raw: dict[str, Any], *, where: str) -> ExpectedConformanceResult:
    rid = str(raw.get("id", "")).strip()
    if not rid:
        raise ValueError(f"conformance expect entry missing id: {where}")
    msg_tokens = raw.get("message_tokens")
    if msg_tokens is not None:
        if not isinstance(msg_tokens, list):
            raise TypeError(f"conformance expect message_tokens must be a list: {where}")
        msg_tokens = [str(x) for x in msg_tokens]
    return ExpectedConformanceResult(
        id=rid,
        status=str(raw.get("status", "")).strip(),
        category=None if raw.get("category") is None else str(raw.get("category")),
        message_tokens=msg_tokens,
    )


def load_expected_results(
    cases_dir: Path,
    *,
    implementation: str = "python",
    case_file_pattern: str | None = None,
    case_formats: set[str] | None = None,
) -> dict[str, ExpectedConformanceResult]:
    out: dict[str, ExpectedConformanceResult] = {}
    impl = str(implementation).strip() or "python"
    for i, (p, c) in enumerate(
        load_external_cases(
            cases_dir,
            formats=case_formats or {"md"},
            md_pattern=case_file_pattern,
        )
    ):
        case_id = str(c.get("id", "")).strip()
        raw_expect = c.get("expect")
        if raw_expect is None:
            raise ValueError(f"conformance case expect is required: {p} cases[{i}]")
        if not isinstance(raw_expect, dict):
            raise TypeError(f"conformance case expect must be a mapping: {p} cases[{i}]")
        portable = raw_expect.get("portable")
        if portable is None:
            portable = {k: v for k, v in raw_expect.items() if k in ("status", "category", "message_tokens")}
        if not isinstance(portable, dict) or "status" not in portable:
            raise ValueError(f"conformance case expect.portable must include status: {p} cases[{i}]")

        merged: dict[str, Any] = {"id": case_id, **portable}
        impl_map = raw_expect.get("impl")
        if impl_map is not None:
            if not isinstance(impl_map, dict):
                raise TypeError(f"conformance case expect.impl must be a mapping: {p} cases[{i}]")
            impl_exp = impl_map.get(impl)
            if impl_exp is not None:
                if not isinstance(impl_exp, dict):
                    raise TypeError(
                        f"conformance case expect.impl.{impl} must be a mapping: {p} cases[{i}]"
                    )
                merged.update({k: v for k, v in impl_exp.items() if k in ("status", "category", "message_tokens")})
        out[case_id] = _parse_expected_entry(merged, where=f"{p} cases[{i}] expect")
    return out


def _category_for_exception(exc: BaseException) -> str:
    if isinstance(exc, AssertionError):
        return "assertion"
    if isinstance(exc, (TypeError, ValueError)):
        return "schema"
    return "runtime"


def _requires_outcome(
    case: dict[str, Any],
    *,
    implementation: str,
    capabilities: set[str],
) -> ConformanceResult | None:
    rid = str(case.get("id", ""))
    raw = case.get("requires")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return ConformanceResult(
            id=rid,
            status="fail",
            category="schema",
            message="requires must be a mapping when provided",
        )
    caps = raw.get("capabilities") or []
    if not isinstance(caps, list):
        return ConformanceResult(
            id=rid,
            status="fail",
            category="schema",
            message="requires.capabilities must be a list",
        )
    needed = [str(x).strip() for x in caps if str(x).strip()]
    when_missing = str(raw.get("when_missing", "fail")).strip().lower() or "fail"
    if when_missing not in {"skip", "fail"}:
        return ConformanceResult(
            id=rid,
            status="fail",
            category="schema",
            message="requires.when_missing must be one of: skip, fail",
        )
    missing = sorted(c for c in needed if c not in capabilities)
    if not missing:
        return None
    if when_missing == "skip":
        return ConformanceResult(id=rid, status="skip", category=None, message=None)
    msg = (
        f"missing required capabilities for implementation '{implementation}': "
        + ", ".join(missing)
    )
    return ConformanceResult(id=rid, status="fail", category="runtime", message=msg)


def run_conformance_cases(
    cases_dir: Path,
    *,
    ctx: SpecRunContext,
    implementation: str = "python",
    capabilities: set[str] | None = None,
    case_file_pattern: str | None = None,
    case_formats: set[str] | None = None,
) -> list[ConformanceResult]:
    impl = str(implementation).strip() or "python"
    caps = set(capabilities) if capabilities is not None else default_capabilities_for(impl)
    results: list[ConformanceResult] = []
    for fixture_path, case in load_conformance_cases(
        cases_dir,
        case_file_pattern=case_file_pattern,
        case_formats=case_formats,
    ):
        test = dict(case)
        case_id = str(test.get("id", ""))
        pre = _requires_outcome(test, implementation=impl, capabilities=caps)
        if pre is not None:
            results.append(pre)
            continue
        try:
            run_case(
                SpecDocTest(doc_path=fixture_path, test=test),
                ctx=ctx,
            )
            results.append(ConformanceResult(id=case_id, status="pass", category=None, message=None))
        except BaseException as e:  # noqa: BLE001
            results.append(
                ConformanceResult(
                    id=case_id,
                    status="fail",
                    category=_category_for_exception(e),
                    message=str(e) or e.__class__.__name__,
                )
            )
    return results


def compare_conformance_results(
    expected: dict[str, ExpectedConformanceResult],
    actual: list[ConformanceResult],
) -> list[str]:
    errs: list[str] = []
    actual_by_id = {r.id: r for r in actual}
    for rid, exp in expected.items():
        got = actual_by_id.get(rid)
        if got is None:
            errs.append(f"missing actual result for id: {rid}")
            continue
        if got.status != exp.status:
            errs.append(f"status mismatch for {rid}: expected={exp.status} actual={got.status}")
        if got.category != exp.category:
            errs.append(f"category mismatch for {rid}: expected={exp.category} actual={got.category}")
        for tok in exp.message_tokens or []:
            if tok not in str(got.message or ""):
                errs.append(f"message token missing for {rid}: {tok}")
    for rid in actual_by_id:
        if rid not in expected:
            errs.append(f"unexpected actual result id: {rid}")
    return errs


def results_to_jsonable(results: list[ConformanceResult]) -> list[dict[str, Any]]:
    return [asdict(r) for r in results]


def report_to_jsonable(results: list[ConformanceResult]) -> dict[str, Any]:
    return {"version": 1, "results": results_to_jsonable(results)}


def validate_conformance_report_payload(payload: Any) -> list[str]:
    errs: list[str] = []
    if not isinstance(payload, dict):
        return ["report payload must be a mapping"]
    if payload.get("version") != 1:
        errs.append("report.version must equal 1")
    results = payload.get("results")
    if not isinstance(results, list):
        errs.append("report.results must be a list")
        return errs
    for i, item in enumerate(results):
        pfx = f"results[{i}]"
        if not isinstance(item, dict):
            errs.append(f"{pfx} must be a mapping")
            continue
        rid = item.get("id")
        if not isinstance(rid, str) or not rid.strip():
            errs.append(f"{pfx}.id must be a non-empty string")
        status = item.get("status")
        if status not in _VALID_STATUS:
            errs.append(f"{pfx}.status must be one of: pass, fail, skip")
        category = item.get("category")
        if status in {"pass", "skip"}:
            if category is not None:
                errs.append(f"{pfx}.category must be null when status={status}")
        elif status == "fail":
            if category not in _VALID_CATEGORY:
                errs.append(f"{pfx}.category must be one of: schema, assertion, runtime when status=fail")
        message = item.get("message")
        if status in {"pass", "skip"}:
            if message is not None:
                errs.append(f"{pfx}.message must be null when status={status}")
        elif status == "fail":
            if not isinstance(message, str) or not message.strip():
                errs.append(f"{pfx}.message must be a non-empty string when status=fail")
    return errs
