from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
import time
from typing import Any, Callable, Mapping, Protocol, cast

from spec_runner.codecs import load_external_cases
from spec_runner.compiler import compile_external_case
from spec_runner.components.chain_engine import execute_case_chain
from spec_runner.doc_parser import SpecDocTest
from spec_runner.internal_model import InternalSpecCase


class RuntimePatcher(Protocol):
    def context(self) -> Any: ...


class RuntimeCapture(Protocol):
    def readouterr(self) -> Any: ...


TypeRunner = Callable[..., None]


class RuntimeProfiler(Protocol):
    def span(self, *, name: str, kind: str, phase: str, attrs: Mapping[str, Any] | None = None) -> Any: ...


@dataclass(frozen=True)
class SpecRunContext:
    tmp_path: Path
    patcher: RuntimePatcher
    capture: RuntimeCapture
    env: Mapping[str, str] | None = None
    chain_state: dict[str, Any] = field(default_factory=dict)
    chain_trace: list[dict[str, Any]] = field(default_factory=list)
    _case_target_values: dict[str, dict[str, Any]] = field(default_factory=dict)
    _case_chain_imports: dict[str, dict[str, Any]] = field(default_factory=dict)
    _case_chain_payloads: dict[str, dict[str, Any]] = field(default_factory=dict)
    _active_case_keys: set[str] = field(default_factory=set)
    profile_enabled: bool = False
    profile_rows: list[dict[str, Any]] = field(default_factory=list)
    profiler: Any | None = None

    def patch_context(self) -> Any:
        return self.patcher.context()

    def read_capture(self) -> Any:
        return self.capture.readouterr()

    def set_case_targets(self, *, case_key: str, targets: Mapping[str, Any]) -> None:
        self._case_target_values[case_key] = dict(targets)

    def get_case_targets(self, *, case_key: str) -> Mapping[str, Any] | None:
        return self._case_target_values.get(case_key)

    def set_case_chain_imports(self, *, case_key: str, imports: Mapping[str, Any]) -> None:
        self._case_chain_imports[case_key] = dict(imports)

    def get_case_chain_imports(self, *, case_key: str) -> Mapping[str, Any]:
        return dict(self._case_chain_imports.get(case_key, {}))

    def set_case_chain_payload(self, *, case_key: str, payload: Mapping[str, Any]) -> None:
        self._case_chain_payloads[case_key] = dict(payload)

    def get_case_chain_payload(self, *, case_key: str) -> Mapping[str, Any]:
        return dict(self._case_chain_payloads.get(case_key, {"state": {}, "trace": [], "imports": {}}))

    def push_active_case(self, case_key: str) -> None:
        if case_key in self._active_case_keys:
            raise RuntimeError(f"recursive case execution detected for {case_key}")
        self._active_case_keys.add(case_key)

    def pop_active_case(self, case_key: str) -> None:
        self._active_case_keys.discard(case_key)

    def add_profile_row(self, row: Mapping[str, Any]) -> None:
        if not self.profile_enabled:
            return
        self.profile_rows.append(dict(row))


def iter_cases(
    spec_dir: Path,
    *,
    file_pattern: str | None = None,
    formats: set[str] | None = None,
) -> list[SpecDocTest]:
    return [
        SpecDocTest(doc_path=doc_path, test=test)
        for doc_path, test in load_external_cases(spec_dir, formats=formats or {"md"}, md_pattern=file_pattern)
    ]


def default_type_runners() -> dict[str, TypeRunner]:
    # Lazy import to avoid circular imports during collection.
    from spec_runner.harnesses.api_http import run as run_api_http
    from spec_runner.harnesses.cli_run import run as run_cli
    from spec_runner.harnesses.text_file import run as run_text_file

    def run_contract_check(case: InternalSpecCase, *, ctx: SpecRunContext) -> None:
        harness = case.harness or {}
        check_cfg = harness.get("check")
        if not isinstance(check_cfg, dict):
            raise RuntimeError("contract.check requires harness.check mapping")
        profile = str(check_cfg.get("profile", "")).strip()
        if profile not in {"text.file", "cli.run", "api.http", "governance.scan"}:
            raise RuntimeError("contract.check harness.check.profile must be one of: text.file, cli.run, api.http, governance.scan")
        if profile == "governance.scan":
            raise RuntimeError("contract.check profile governance.scan is owned by governance runner")
        config = check_cfg.get("config")
        if config is None:
            config_map: dict[str, Any] = {}
        elif isinstance(config, dict):
            config_map = dict(config)
        else:
            raise RuntimeError("contract.check harness.check.config must be a mapping")
        raw = dict(case.raw_case)
        raw["type"] = profile
        merged_harness = dict(harness)
        merged_harness.pop("check", None)
        raw["harness"] = merged_harness
        for k, v in config_map.items():
            if k in {"id", "type", "title", "purpose", "contract", "when", "harness", "requires", "expect", "assert_health"}:
                continue
            raw[k] = v
        adapted_case = replace(
            case,
            type=profile,
            raw_case=raw,
            harness=merged_harness,
        )
        if profile == "text.file":
            run_text_file(adapted_case, ctx=ctx)
            return
        if profile == "cli.run":
            run_cli(adapted_case, ctx=ctx)
            return
        if profile == "api.http":
            run_api_http(adapted_case, ctx=ctx)
            return
        raise RuntimeError(f"unsupported contract.check profile: {profile}")

    def run_contract_export(_: InternalSpecCase, *, ctx: SpecRunContext) -> None:
        del ctx
        return

    def run_contract_job(case: InternalSpecCase, *, ctx: SpecRunContext) -> None:
        harness = case.harness or {}
        jobs = harness.get("jobs")
        if not isinstance(jobs, dict):
            raise RuntimeError("contract.job requires harness.jobs mapping")
        del ctx
        return

    return {
        "contract.check": run_contract_check,
        "contract.export": run_contract_export,
        "contract.job": run_contract_job,
    }


def _to_internal_case(case: SpecDocTest | InternalSpecCase) -> InternalSpecCase:
    if isinstance(case, InternalSpecCase):
        return case
    return compile_external_case(case.test, doc_path=case.doc_path)


def run_case(
    case: SpecDocTest | InternalSpecCase,
    *,
    ctx: SpecRunContext,
    type_runners: Mapping[str, TypeRunner] | None = None,
) -> None:
    runners = default_type_runners()
    if type_runners:
        runners.update(type_runners)
    if isinstance(case, InternalSpecCase):
        type_ = case.type
    else:
        type_ = str(case.test["type"])
    fn = runners.get(type_)
    if not fn:
        doc_path = case.doc_path if isinstance(case, SpecDocTest) else case.doc_path
        raise RuntimeError(f"unknown contract-spec type: {type_} (from {doc_path})")

    internal_case = _to_internal_case(case)
    case_key = f"{internal_case.doc_path.resolve().as_posix()}::{internal_case.id}"
    started = time.perf_counter()
    chain_started: float | None = None
    harness_started: float | None = None
    chain_elapsed_ms = 0.0
    harness_elapsed_ms = 0.0
    status = "pass"
    error: str | None = None
    ctx.push_active_case(case_key)
    try:
        raw_profiler = getattr(ctx, "profiler", None)
        profiler = cast(RuntimeProfiler | None, raw_profiler)
        case_span_cm = (
            profiler.span(
                name="case.run",
                kind="case",
                phase="case.run",
                attrs={
                    "case_id": internal_case.id,
                    "case_type": internal_case.type,
                    "doc_path": internal_case.doc_path.as_posix(),
                },
            )
            if profiler is not None
            else None
        )
        if case_span_cm is None:
            chain_started = time.perf_counter()
            execute_case_chain(
                internal_case,
                ctx=ctx,
                run_case_fn=lambda chained_case: run_case(chained_case, ctx=ctx, type_runners=type_runners),
            )
            chain_elapsed_ms = (time.perf_counter() - chain_started) * 1000.0
            harness_started = time.perf_counter()
            if type_ in {"contract.check", "contract.export", "contract.job"}:
                fn(internal_case, ctx=ctx)
                harness_elapsed_ms = (time.perf_counter() - harness_started) * 1000.0
                return
            fn(case, ctx=ctx)
            harness_elapsed_ms = (time.perf_counter() - harness_started) * 1000.0
            return

        with case_span_cm:
            assert profiler is not None
            chain_started = time.perf_counter()
            chain_span_cm = profiler.span(
                name="case.chain",
                kind="chain",
                phase="case.chain",
                attrs={"case_id": internal_case.id},
            )
            with chain_span_cm:
                execute_case_chain(
                    internal_case,
                    ctx=ctx,
                    run_case_fn=lambda chained_case: run_case(chained_case, ctx=ctx, type_runners=type_runners),
                )
            chain_elapsed_ms = (time.perf_counter() - chain_started) * 1000.0
            harness_started = time.perf_counter()
            harness_span_cm = profiler.span(
                name="case.harness",
                kind="harness",
                phase="case.harness",
                attrs={"case_id": internal_case.id, "case_type": internal_case.type},
            )
            with harness_span_cm:
                if type_ in {"contract.check", "contract.export", "contract.job"}:
                    fn(internal_case, ctx=ctx)
                    harness_elapsed_ms = (time.perf_counter() - harness_started) * 1000.0
                    return
                fn(case, ctx=ctx)
                harness_elapsed_ms = (time.perf_counter() - harness_started) * 1000.0
    except BaseException as exc:  # noqa: BLE001
        status = "fail"
        error = str(exc)
        if chain_started is not None and chain_elapsed_ms <= 0.0:
            chain_elapsed_ms = (time.perf_counter() - chain_started) * 1000.0
        if harness_started is not None and harness_elapsed_ms <= 0.0:
            harness_elapsed_ms = (time.perf_counter() - harness_started) * 1000.0
        raise
    finally:
        total_elapsed_ms = (time.perf_counter() - started) * 1000.0
        ctx.add_profile_row(
            {
                "case_id": internal_case.id,
                "case_type": internal_case.type,
                "doc_path": internal_case.doc_path.as_posix(),
                "case_key": case_key,
                "status": status,
                "duration_ms": round(float(total_elapsed_ms), 3),
                "chain_duration_ms": round(float(chain_elapsed_ms), 3),
                "harness_duration_ms": round(float(harness_elapsed_ms), 3),
                "error": error,
            }
        )
        ctx.pop_active_case(case_key)
