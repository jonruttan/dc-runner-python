from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from spec_runner.codecs import load_external_cases
from spec_runner.compiler import compile_external_case
from spec_runner.internal_model import InternalSpecCase
from spec_runner.spec_lang import _Closure, _Env, compile_symbol_bindings, limits_from_harness
from spec_runner.spec_lang_yaml_ast import SpecLangYamlAstError, compile_yaml_expr_to_sexpr
from spec_runner.spec_domain import normalize_case_domain, normalize_export_symbol
from spec_runner.virtual_paths import contract_root_for, parse_external_ref, resolve_contract_path

_CASE_ID_PART = re.compile(r"^[A-Za-z0-9._:-]+$")
_STEP_CLASS_VALUES = {"MUST", "MAY", "MUST_NOT"}
_RESERVED_IMPORT_NAMES = {"subject", "if", "let", "fn", "call", "var"}
_CHAIN_PRODUCER_EXPORT_KEYS = {"as", "from", "path", "params", "required"}
_PRODUCER_EXPORT_CACHE_LOCK = threading.RLock()
_PRODUCER_EXPORT_CACHE: dict[tuple[str, str], dict[str, Any]] = {}
_DOC_CASES_CACHE_LOCK = threading.RLock()
_DOC_CASES_CACHE: dict[tuple[str, int, int], list[InternalSpecCase]] = {}
_DOC_CASE_INDEX_CACHE: dict[tuple[str, int, int], dict[str, list[InternalSpecCase]]] = {}


@dataclass(frozen=True)
class ChainRef:
    raw: str
    path: str | None
    case_id: str | None


@dataclass(frozen=True)
class ChainProducedImport:
    from_source: str
    path: str | None
    params: tuple[str, ...]
    required: bool


@dataclass(frozen=True)
class ChainStep:
    id: str
    class_name: str
    ref: ChainRef
    allow_continue: bool


@dataclass(frozen=True)
class ChainImport:
    from_id: str
    names: tuple[str, ...]
    aliases: dict[str, str]


def parse_spec_ref(raw_ref: str) -> ChainRef:
    raw = str(raw_ref).strip()
    if not raw:
        raise ValueError("harness.chain.steps[*].ref must be a non-empty string")
    if "#" in raw:
        path_part, case_part = raw.split("#", 1)
        path = path_part.strip() or None
        case_id = case_part.strip()
        if not case_id:
            raise ValueError("harness.chain.steps[*].ref fragment case_id must be non-empty when '#' is present")
        if not _CASE_ID_PART.match(case_id):
            raise ValueError(
                "harness.chain.steps[*].ref fragment case_id must match [A-Za-z0-9._:-]+"
            )
        if path is not None and parse_external_ref(path) is not None:
            raise ValueError("harness.chain.steps[*].ref path must not be external://")
        return ChainRef(raw=raw, path=path, case_id=case_id)
    if parse_external_ref(raw) is not None:
        raise ValueError("harness.chain.steps[*].ref path must not be external://")
    return ChainRef(raw=raw, path=raw, case_id=None)


def _parse_params(
    raw: object,
    *,
    step_idx: int,
    import_idx: int,
    import_name: str,
) -> tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise TypeError(
            f"harness.chain.steps[{step_idx}].imports[{import_idx}].params must be a list when provided"
        )
    out: list[str] = []
    for param_idx, item in enumerate(raw):
        param = str(item).strip()
        if not param:
            raise ValueError(
                f"harness.chain.steps[{step_idx}].imports[{import_idx}].params[{param_idx}] must be non-empty"
            )
        if param in out:
            raise ValueError(
                f"harness.chain.steps[{step_idx}].imports[{import_idx}] duplicate param for {import_name}: {param}"
            )
        out.append(param)
    return tuple(out)


def _expand_producer_exports(
    raw_exports: object,
    *,
    field_prefix: str,
    domain: str | None = None,
) -> dict[str, ChainProducedImport]:
    if raw_exports is None:
        return {}
    if not isinstance(raw_exports, list):
        raise TypeError(f"{field_prefix} must be a list (canonical form)")

    expanded: dict[str, ChainProducedImport] = {}
    for idx, raw_entry in enumerate(raw_exports):
        if not isinstance(raw_entry, dict):
            raise TypeError(f"{field_prefix}[{idx}] must be a mapping")
        unknown = sorted(str(k) for k in raw_entry.keys() if str(k) not in _CHAIN_PRODUCER_EXPORT_KEYS)
        if unknown:
            raise ValueError(
                f"{field_prefix}[{idx}] entry has unsupported keys: {', '.join(unknown)}"
            )

        raw_export_name = str(raw_entry.get("as", "")).strip()
        if not raw_export_name:
            raise ValueError(f"{field_prefix}[{idx}].as is required")
        export_name = normalize_export_symbol(domain, raw_export_name)
        if export_name in expanded:
            raw_domain = domain if domain is not None else "<none>"
            raise ValueError(
                f"{field_prefix} duplicate key after domain prefix "
                f"(raw_as={raw_export_name}, domain={raw_domain}, canonical={export_name})"
            )

        from_source = str(raw_entry.get("from", "")).strip()
        if from_source != "assert.function":
            raise ValueError(
                f"{field_prefix}[{idx}].from must be assert.function"
            )

        export_path = raw_entry.get("path")
        if export_path is not None and not isinstance(export_path, str):
            raise TypeError(f"{field_prefix}[{idx}].path must be a string when provided")
        path_val = str(export_path or "").strip().lstrip("/")
        if not path_val:
            raise ValueError(f"{field_prefix}[{idx}].path is required for from=assert.function")

        params = _parse_params(
            raw_entry.get("params"),
            step_idx=0,
            import_idx=idx,
            import_name=export_name,
        )

        raw_required = raw_entry.get("required", True)
        if not isinstance(raw_required, bool):
            raise TypeError(f"{field_prefix}[{idx}].required must be a bool when provided")

        expanded[export_name] = ChainProducedImport(
            from_source=from_source,
            path=path_val,
            params=params,
            required=raw_required,
        )
    return expanded


def _lower_harness_use(harness: dict[str, Any]) -> dict[str, Any] | None:
    raw_use = harness.get("use")
    if raw_use is None:
        return None
    if not isinstance(raw_use, list):
        raise TypeError("harness.use must be a non-empty list")
    if not raw_use:
        raise TypeError("harness.use must be a non-empty list")

    steps: list[dict[str, Any]] = []
    imports: list[dict[str, Any]] = []
    seen_aliases: set[str] = set()
    for idx, item in enumerate(raw_use):
        if not isinstance(item, dict):
            raise TypeError(f"harness.use[{idx}] must be a mapping")
        ref = str(item.get("ref", "")).strip()
        alias = str(item.get("as", "")).strip()
        symbols = item.get("symbols")
        if not ref:
            raise ValueError(f"harness.use[{idx}].ref must be a non-empty string")
        if not alias:
            raise ValueError(f"harness.use[{idx}].as must be a non-empty string")
        if alias in seen_aliases:
            raise ValueError(f"harness.use has duplicate alias: {alias}")
        seen_aliases.add(alias)
        if not isinstance(symbols, list) or not symbols:
            raise TypeError(f"harness.use[{idx}].symbols must be a non-empty list")
        names: list[str] = []
        for j, raw_name in enumerate(symbols):
            symbol = str(raw_name).strip()
            if not symbol:
                raise ValueError(f"harness.use[{idx}].symbols[{j}] must be non-empty")
            names.append(symbol)
        steps.append(
            {
                "id": alias,
                "class": "MUST",
                "ref": ref,
            }
        )
        imports.append(
            {
                "from": alias,
                "names": names,
            }
        )
    return {"steps": steps, "imports": imports, "fail_fast": True}


def compile_chain_plan(case: InternalSpecCase) -> tuple[list[ChainStep], list[ChainImport], bool]:
    harness = case.harness or {}
    raw_chain = harness.get("chain")
    lowered_from_use = _lower_harness_use(harness)
    if raw_chain is not None and lowered_from_use is not None:
        raise ValueError("harness.chain and harness.use are mutually exclusive")
    if raw_chain is None and lowered_from_use is not None:
        raw_chain = lowered_from_use
    if raw_chain is None:
        return [], [], True
    if not isinstance(raw_chain, dict):
        raise TypeError("harness.chain must be a mapping")
    if "exports" in raw_chain:
        raise ValueError("harness.chain.exports is forbidden; use harness.exports")

    raw_fail_fast = raw_chain.get("fail_fast", True)
    if not isinstance(raw_fail_fast, bool):
        raise TypeError("harness.chain.fail_fast must be a bool when provided")
    fail_fast = bool(raw_fail_fast)

    raw_steps = raw_chain.get("steps", [])
    if raw_steps is None:
        raw_steps = []
    if not isinstance(raw_steps, list):
        raise TypeError("harness.chain.steps must be a list when provided")

    seen_ids: set[str] = set()
    steps: list[ChainStep] = []
    for idx, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise TypeError(f"harness.chain.steps[{idx}] must be a mapping")

        step_id = str(raw.get("id", "")).strip()
        if not step_id:
            raise ValueError(f"harness.chain.steps[{idx}].id must be a non-empty string")
        if step_id in seen_ids:
            raise ValueError(f"harness.chain.steps has duplicate id: {step_id}")
        seen_ids.add(step_id)

        class_name = str(raw.get("class", "")).strip()
        if class_name not in _STEP_CLASS_VALUES:
            raise ValueError(
                f"harness.chain.steps[{idx}].class must be one of: MUST, MAY, MUST_NOT"
            )

        raw_ref = raw.get("ref")
        if isinstance(raw_ref, dict):
            raise TypeError(
                f"harness.chain.steps[{idx}].ref legacy mapping format is not supported; use string [path][#case_id]"
            )
        if not isinstance(raw_ref, str):
            raise TypeError(f"harness.chain.steps[{idx}].ref must be a string")
        parsed_ref = parse_spec_ref(raw_ref)

        if "imports" in raw:
            raise ValueError(
                f"harness.chain.steps[{idx}].imports is forbidden; producer symbol declarations must be on producer harness.exports"
            )
        if "exports" in raw:
            raise ValueError(
                f"harness.chain.steps[{idx}].exports is forbidden; producer symbol declarations must be on producer harness.exports"
            )

        raw_allow_continue = raw.get("allow_continue", False)
        if not isinstance(raw_allow_continue, bool):
            raise TypeError(f"harness.chain.steps[{idx}].allow_continue must be a bool when provided")

        steps.append(
            ChainStep(
                id=step_id,
                class_name=class_name,
                ref=parsed_ref,
                allow_continue=raw_allow_continue,
            )
        )

    raw_imports = raw_chain.get("imports", [])
    if raw_imports is None:
        raw_imports = []
    if not isinstance(raw_imports, list):
        raise TypeError("harness.chain.imports must be a list when provided")

    chain_imports: list[ChainImport] = []
    local_seen: set[str] = set()
    step_ids = {x.id for x in steps}
    for idx, item in enumerate(raw_imports):
        if not isinstance(item, dict):
            raise TypeError(f"harness.chain.imports[{idx}] must be a mapping")
        from_id = str(item.get("from", "")).strip()
        if not from_id:
            raise ValueError(f"harness.chain.imports[{idx}].from must be non-empty")
        if from_id not in step_ids:
            raise ValueError(
                f"harness.chain.imports[{idx}].from must reference existing step id"
            )

        raw_names = item.get("names")
        if not isinstance(raw_names, list) or not raw_names:
            raise TypeError(f"harness.chain.imports[{idx}].names must be a non-empty list")
        names: list[str] = []
        for j, raw_name in enumerate(raw_names):
            name = str(raw_name).strip()
            if not name:
                raise ValueError(f"harness.chain.imports[{idx}].names[{j}] must be non-empty")
            names.append(name)

        raw_aliases = item.get("as", {})
        if raw_aliases is None:
            raw_aliases = {}
        if not isinstance(raw_aliases, dict):
            raise TypeError(f"harness.chain.imports[{idx}].as must be a mapping when provided")

        aliases: dict[str, str] = {}
        for raw_from, raw_to in raw_aliases.items():
            from_name = str(raw_from).strip()
            to_name = str(raw_to).strip()
            if not from_name or not to_name:
                raise ValueError(
                    f"harness.chain.imports[{idx}].as keys and values must be non-empty strings"
                )
            if from_name not in names:
                raise ValueError(
                    f"harness.chain.imports[{idx}].as references name not in names: {from_name}"
                )
            aliases[from_name] = to_name

        for name in names:
            local = aliases.get(name, name)
            if local in _RESERVED_IMPORT_NAMES:
                raise ValueError(
                    f"harness.chain.imports[{idx}] local binding collides with reserved name: {local}"
                )
            if local in local_seen:
                raise ValueError(
                    f"harness.chain.imports[{idx}] local binding collision for name: {local}"
                )
            local_seen.add(local)

        chain_imports.append(ChainImport(from_id=from_id, names=tuple(names), aliases=aliases))

    return steps, chain_imports, fail_fast


def _producer_case_exports(producer_case: InternalSpecCase) -> dict[str, ChainProducedImport]:
    harness = producer_case.harness or {}
    try:
        domain = normalize_case_domain((producer_case.raw_case or {}).get("domain"))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"producer case {producer_case.id} has invalid domain ({exc})"
        ) from exc
    return _expand_producer_exports(
        harness.get("exports"),
        field_prefix="harness.exports",
        domain=domain,
    )


def _resolve_ref_path(*, ref_path: str, current_case: InternalSpecCase) -> Path:
    root = contract_root_for(current_case.doc_path)
    if ref_path.startswith("/"):
        return resolve_contract_path(root, ref_path, field="harness.chain.steps.ref")
    doc_parent = current_case.doc_path.resolve().parent
    resolved = (doc_parent / ref_path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("harness.chain.steps.ref escapes contract root") from exc
    return resolved


def _load_doc_internal_cases(
    doc_path: Path,
    *,
    doc_cases_cache: dict[str, list[InternalSpecCase]],
    case_index_cache: dict[str, dict[str, list[InternalSpecCase]]],
) -> list[InternalSpecCase]:
    resolved = doc_path.resolve()
    local_key = resolved.as_posix()
    cached = doc_cases_cache.get(local_key)
    if cached is not None:
        return cached
    try:
        st = resolved.stat()
        global_key = (resolved.as_posix(), int(st.st_mtime_ns), int(st.st_size))
    except OSError:
        global_key = (resolved.as_posix(), -1, -1)

    with _DOC_CASES_CACHE_LOCK:
        global_cached = _DOC_CASES_CACHE.get(global_key)
        global_index = _DOC_CASE_INDEX_CACHE.get(global_key)
    if global_cached is not None and global_index is not None:
        doc_cases_cache[local_key] = global_cached
        case_index_cache[local_key] = global_index
        return global_cached

    docs = load_external_cases(doc_path, formats={"md"})
    compiled = [compile_external_case(test, doc_path=source_path) for source_path, test in docs]
    doc_cases_cache[local_key] = compiled
    case_index: dict[str, list[InternalSpecCase]] = {}
    for spec_case in compiled:
        case_index.setdefault(spec_case.id, []).append(spec_case)
    case_index_cache[local_key] = case_index
    with _DOC_CASES_CACHE_LOCK:
        _DOC_CASES_CACHE[global_key] = compiled
        _DOC_CASE_INDEX_CACHE[global_key] = case_index
    return compiled


def resolve_chain_reference(
    step: ChainStep,
    *,
    current_case: InternalSpecCase,
    doc_cases_cache: dict[str, list[InternalSpecCase]],
    case_index_cache: dict[str, dict[str, list[InternalSpecCase]]],
) -> list[InternalSpecCase]:
    if step.ref.path:
        resolved = _resolve_ref_path(ref_path=step.ref.path, current_case=current_case)
        if not resolved.exists() or not resolved.is_file():
            raise ValueError(f"chain ref path does not exist as file: {step.ref.path}")
        docs = _load_doc_internal_cases(
            resolved,
            doc_cases_cache=doc_cases_cache,
            case_index_cache=case_index_cache,
        )
        if step.ref.case_id:
            case_index = case_index_cache.get(resolved.resolve().as_posix(), {})
            filtered = list(case_index.get(step.ref.case_id, []))
            if not filtered:
                raise ValueError(
                    f"chain step {step.id} could not resolve case_id {step.ref.case_id} in {step.ref.path}"
                )
            if len(filtered) > 1:
                raise ValueError(
                    f"chain step {step.id} resolved duplicate case_id {step.ref.case_id} in {step.ref.path}"
                )
            return [filtered[0]]
        return docs

    assert step.ref.case_id is not None
    _load_doc_internal_cases(
        current_case.doc_path,
        doc_cases_cache=doc_cases_cache,
        case_index_cache=case_index_cache,
    )
    local_index = case_index_cache.get(current_case.doc_path.resolve().as_posix(), {})
    filtered = list(local_index.get(step.ref.case_id, []))
    if not filtered:
        raise ValueError(f"chain step {step.id} could not resolve local case_id {step.ref.case_id}")
    if len(filtered) > 1:
        raise ValueError(f"chain step {step.id} resolved duplicate local case_id {step.ref.case_id}")
    return [filtered[0]]


def _compile_assert_function(
    *,
    step: ChainStep,
    import_name: str,
    producer: ChainProducedImport,
    producer_case: InternalSpecCase,
) -> _Closure:
    producer_key = str(producer.path or "").strip().lstrip("/")
    if not producer_key:
        raise ValueError(
            f"chain step {step.id} import {import_name} requires non-empty path for from=assert.function"
        )
    raw_assert = producer_case.raw_case.get("contract")
    if isinstance(raw_assert, list):
        source_step: dict[str, Any] | None = None
        for item in raw_assert:
            if not isinstance(item, dict):
                continue
            if str(item.get("id", "")).strip() == producer_key:
                source_step = item
                break
        if source_step is not None:
            if str(source_step.get("class", "")).strip() != "MUST":
                raise ValueError(
                    f"chain step {step.id} import {import_name} requires producer contract step class=MUST"
                )

            checks = source_step.get("asserts")
            if not isinstance(checks, list) or not checks:
                raise ValueError(
                    f"chain step {step.id} import {import_name} producer step {producer_key} requires non-empty asserts"
                )

            exprs: list[Any] = []
            for idx, raw_check in enumerate(checks):
                if not isinstance(raw_check, dict):
                    raise ValueError(
                        f"chain step {step.id} import {import_name} producer check {idx} must be expression mapping"
                    )
                if set(raw_check.keys()) == {"evaluate"}:
                    expr_raw = raw_check.get("evaluate")
                else:
                    expr_raw = raw_check
                try:
                    expr = compile_yaml_expr_to_sexpr(
                        expr_raw,
                        field_path=f"harness.chain.steps[{step.id}].imports.{import_name}.producer_checks[{idx}]",
                    )
                except SpecLangYamlAstError as exc:
                    raise ValueError(str(exc)) from exc
                exprs.append(expr)

            if len(exprs) == 1:
                body = exprs[0]
            else:
                body = exprs[-1]
                for expr in reversed(exprs[:-1]):
                    body = ["std.logic.and", expr, body]

            return _Closure(params=tuple(producer.params), body=body, env=_Env(vars={}, parent=None))

    raise ValueError(
        f"chain step {step.id} import {import_name} could not resolve assert.function path {producer_key} in {producer_case.id}"
    )


def _compile_assert_function_expr(
    *,
    step: ChainStep,
    import_name: str,
    producer: ChainProducedImport,
    producer_case: InternalSpecCase,
) -> list[Any]:
    closure = _compile_assert_function(
        step=step,
        import_name=import_name,
        producer=producer,
        producer_case=producer_case,
    )
    return ["fn", list(closure.params), closure.body]


def _producer_cache_key(producer_case: InternalSpecCase) -> tuple[str, str]:
    resolved = producer_case.doc_path.resolve().as_posix()
    raw = producer_case.raw_case
    try:
        # Stable per-case signature covering contract and chain export declarations.
        import json

        signature = json.dumps(
            {
                "contract": raw.get("contract"),
                "chain": (raw.get("harness") or {}).get("chain") if isinstance(raw.get("harness"), dict) else None,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    except Exception:
        signature = repr(raw.get("contract")) + "|" + repr((raw.get("harness") or {}).get("chain"))
    return (f"{resolved}::{producer_case.id}", signature)


def _get_producer_export_exprs(
    *,
    step: ChainStep,
    producer_case: InternalSpecCase,
) -> dict[str, Any]:
    cache_key = _producer_cache_key(producer_case)
    with _PRODUCER_EXPORT_CACHE_LOCK:
        cached = _PRODUCER_EXPORT_CACHE.get(cache_key)
        if cached is not None:
            return dict(cached)

    exports = _producer_case_exports(producer_case)
    exprs: dict[str, Any] = {}
    required_names: set[str] = set()
    for export_name, producer in exports.items():
        if producer.from_source != "assert.function":
            continue
        if producer.required:
            required_names.add(export_name)
        exprs[export_name] = _compile_assert_function_expr(
            step=step,
            import_name=export_name,
            producer=producer,
            producer_case=producer_case,
        )

    for required_name in sorted(required_names):
        if required_name not in exprs:
            raise ValueError(
                f"chain step {step.id} import {required_name} could not be resolved from producer refs"
            )
    if not exprs:
        with _PRODUCER_EXPORT_CACHE_LOCK:
            _PRODUCER_EXPORT_CACHE[cache_key] = {}
        return {}
    with _PRODUCER_EXPORT_CACHE_LOCK:
        _PRODUCER_EXPORT_CACHE[cache_key] = dict(exprs)
    return dict(exprs)


def _extract_assert_function_imports(
    *,
    step: ChainStep,
    refs: list[InternalSpecCase],
) -> dict[str, Any]:
    merged_exprs: dict[str, Any] = {}
    required_exports: set[str] = set()
    deferred_errors: dict[str, Exception] = {}
    for ref_case in refs:
        exports = _producer_case_exports(ref_case)
        for export_name, producer in exports.items():
            if producer.from_source == "assert.function" and producer.required:
                required_exports.add(export_name)
        try:
            producer_exprs = _get_producer_export_exprs(step=step, producer_case=ref_case)
        except Exception:
            for export_name, producer in exports.items():
                if producer.from_source == "assert.function" and producer.required:
                    deferred_errors.setdefault(
                        export_name,
                        ValueError(
                            f"chain step {step.id} import {export_name} could not be resolved from producer refs"
                        ),
                    )
            continue
        for export_name, expr in producer_exprs.items():
            merged_exprs.setdefault(export_name, expr)

    unresolved_required = sorted(name for name in required_exports if name not in merged_exprs)
    if unresolved_required:
        first = unresolved_required[0]
        raise deferred_errors.get(
            first,
            ValueError(
                f"chain step {step.id} import {first} could not be resolved from producer refs"
            ),
        )
    if not merged_exprs:
        return {}
    try:
        return compile_symbol_bindings(merged_exprs, limits=limits_from_harness({}))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            f"chain step {step.id} could not compile producer export symbols"
        ) from exc


def execute_chain_plan(
    case: InternalSpecCase,
    *,
    ctx,
    run_case_fn: Callable[[InternalSpecCase], None],
) -> None:
    steps, chain_imports, fail_fast = compile_chain_plan(case)
    if not steps:
        return

    doc_cases_cache: dict[str, list[InternalSpecCase]] = {}
    case_index_cache: dict[str, dict[str, list[InternalSpecCase]]] = {}
    case_key = f"{case.doc_path.resolve().as_posix()}::{case.id}"

    ctx.chain_state.clear()
    ctx.chain_trace.clear()

    for step in steps:
        refs = resolve_chain_reference(
            step,
            current_case=case,
            doc_cases_cache=doc_cases_cache,
            case_index_cache=case_index_cache,
        )

        step_values: dict[str, Any] = {}
        compile_only_step = any(ci.from_id == step.id for ci in chain_imports)

        if compile_only_step:
            compile_success = True
            failure: Exception | None = None
            try:
                step_values.update(_extract_assert_function_imports(step=step, refs=refs))
                if not step_values:
                    raise ValueError(
                        f"chain step {step.id} did not expose producer exports"
                    )
            except Exception as exc:
                compile_success = False
                failure = exc

            passed = (not compile_success) if step.class_name == "MUST_NOT" else compile_success
            ctx.chain_trace.append(
                {
                    "step_id": step.id,
                    "class": step.class_name,
                    "ref_case_id": refs[0].id if refs else "",
                    "ref_doc_path": "/" + (refs[0].doc_path.resolve().as_posix().lstrip("/") if refs else ""),
                    "status": "pass" if passed else "fail",
                }
            )
            if not passed and step.class_name == "MUST" and failure is not None and fail_fast and not step.allow_continue:
                raise failure
            if not passed and step.class_name == "MUST_NOT" and fail_fast and not step.allow_continue:
                raise RuntimeError(f"chain step {step.id} with class 'MUST_NOT' unexpectedly succeeded")

            if step.class_name != "MUST_NOT" and compile_success:
                ctx.chain_state[step.id] = dict(step_values)
            else:
                ctx.chain_state[step.id] = {}
            continue

        # runtime imports from executed target values
        at_least_one_passed = False
        last_failure: Exception | None = None
        for ref_case in refs:
            ref_key = f"{ref_case.doc_path.resolve().as_posix()}::{ref_case.id}"
            cur_key = f"{case.doc_path.resolve().as_posix()}::{case.id}"
            if ref_key == cur_key:
                raise RuntimeError(f"chain step {step.id} references current case recursively")

            passed = False
            runtime_failure: Exception | None = None
            try:
                run_case_fn(ref_case)
                if step.class_name == "MUST_NOT":
                    passed = False
                else:
                    passed = True
            except Exception as exc:
                runtime_failure = exc
                passed = step.class_name == "MUST_NOT"

            ctx.chain_trace.append(
                {
                    "step_id": step.id,
                    "class": step.class_name,
                    "ref_case_id": ref_case.id,
                    "ref_doc_path": "/" + ref_case.doc_path.resolve().as_posix().lstrip("/"),
                    "status": "pass" if passed else "fail",
                }
            )

            if passed:
                at_least_one_passed = True
            if runtime_failure is not None:
                last_failure = runtime_failure

            if step.class_name == "MUST" and not passed and fail_fast and not step.allow_continue:
                raise runtime_failure if runtime_failure is not None else RuntimeError(f"chain step {step.id} failed")
            if step.class_name == "MAY" and passed:
                break
            if step.class_name == "MUST_NOT" and not passed and fail_fast and not step.allow_continue:
                raise RuntimeError(
                    f"chain step {step.id} with class 'MUST_NOT' unexpectedly succeeded"
                )

        if step.class_name == "MAY" and not at_least_one_passed and fail_fast and not step.allow_continue:
            if last_failure is not None:
                raise last_failure
            raise RuntimeError(f"chain step {step.id} with class 'MAY' had no successful references")

        if step.class_name == "MUST_NOT":
            ctx.chain_state[step.id] = {}
        else:
            ctx.chain_state[step.id] = dict(step_values)

    resolved_imports: dict[str, Any] = {}
    for chain_import in chain_imports:
        state = ctx.chain_state.get(chain_import.from_id, {})
        for name in chain_import.names:
            if name not in state:
                raise ValueError(
                    f"harness.chain.imports from {chain_import.from_id} missing export {name}"
                )
            local = chain_import.aliases.get(name, name)
            resolved_imports[local] = state[name]

    ctx.set_case_chain_imports(case_key=case_key, imports=resolved_imports)
    ctx.set_case_chain_payload(
        case_key=case_key,
        payload={
            "state": dict(ctx.chain_state),
            "trace": list(ctx.chain_trace),
            "imports": dict(resolved_imports),
        },
    )


def execute_case_chain(
    case: InternalSpecCase,
    *,
    ctx,
    run_case_fn: Callable[[InternalSpecCase], None],
) -> None:
    execute_chain_plan(case, ctx=ctx, run_case_fn=run_case_fn)
