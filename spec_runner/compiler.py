from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, cast

from spec_runner.internal_model import GroupNode, InternalAssertNode, InternalSpecCase, PredicateLeaf
from spec_runner.schema_validator import validate_case_shape
from spec_runner.spec_domain import normalize_case_domain, normalize_export_symbol
from spec_runner.spec_lang_yaml_ast import SpecLangYamlAstError, compile_yaml_expr_to_sexpr

_LIBRARY_DOC_ALLOWED_KEYS = {
    "summary",
    "description",
    "params",
    "returns",
    "errors",
    "examples",
    "portability",
    "see_also",
    "since",
    "deprecated",
}

_CASE_DOC_ALLOWED_KEYS = {
    "summary",
    "description",
    "audience",
    "since",
    "tags",
    "see_also",
    "deprecated",
}


def _compile_assert_expr_leaf(
    raw_expr: Any,
    *,
    target: str | None,
    imports: dict[str, dict[str, Any]],
    assert_path: str,
) -> PredicateLeaf:
    if not isinstance(raw_expr, dict) or not raw_expr:
        raise ValueError(f"{assert_path} must be a non-empty expression mapping")
    if "evaluate" in raw_expr:
        raise ValueError(f"{assert_path} must not use evaluate wrapper; place operator mapping directly in assert")
    try:
        expr = compile_yaml_expr_to_sexpr(raw_expr, field_path=assert_path)
    except SpecLangYamlAstError as exc:
        raise ValueError(str(exc)) from exc
    # Universal core operator contract: compile-only sugar normalizes to evaluate.
    supported = {"evaluate"}
    op = "evaluate"
    if op == "evaluate":
        pass
    if op not in supported:
        raise ValueError(f"{assert_path} unsupported operator: {op}")
    return PredicateLeaf(
        target=target,
        subject_key=None,
        imports=imports,
        op=op,
        expr=expr,
        assert_path=assert_path,
    )


def _validate_contract_export_docs(raw_case: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    case_id = str(raw_case.get("id", "")).strip() or "<unknown>"
    try:
        case_domain = normalize_case_domain(raw_case.get("domain"))
    except (TypeError, ValueError) as exc:
        issues.append(f"case {case_id}: {exc}")
        case_domain = None
    root_doc = raw_case.get("doc")
    if not isinstance(root_doc, dict):
        issues.append(f"case {case_id}: contract.export requires root doc mapping")
    else:
        unknown_root_doc = sorted(str(k) for k in root_doc.keys() if str(k) not in _CASE_DOC_ALLOWED_KEYS)
        if unknown_root_doc:
            issues.append(
                f"case {case_id}: doc has unsupported keys: {', '.join(unknown_root_doc)}"
            )
        for field in ("summary", "description", "audience", "since"):
            if not str(root_doc.get(field, "")).strip():
                issues.append(f"case {case_id}: doc.{field} must be non-empty")
        tags = root_doc.get("tags")
        if tags is not None and (
            not isinstance(tags, list) or any(not isinstance(x, str) or not str(x).strip() for x in tags)
        ):
            issues.append(f"case {case_id}: doc.tags must be list of non-empty strings when provided")
        see_also = root_doc.get("see_also")
        if see_also is not None and (
            not isinstance(see_also, list)
            or any(not isinstance(x, str) or not str(x).strip() for x in see_also)
        ):
            issues.append(f"case {case_id}: doc.see_also must be list of non-empty strings when provided")
        deprecated = root_doc.get("deprecated")
        if deprecated is not None:
            if not isinstance(deprecated, dict):
                issues.append(f"case {case_id}: doc.deprecated must be mapping when provided")
            else:
                if not str(deprecated.get("replacement", "")).strip():
                    issues.append(f"case {case_id}: doc.deprecated.replacement must be non-empty")
                if not str(deprecated.get("reason", "")).strip():
                    issues.append(f"case {case_id}: doc.deprecated.reason must be non-empty")

    library = raw_case.get("library")
    if not isinstance(library, dict):
        return [*issues, f"case {case_id}: contract.export requires library mapping"]
    lid = str(library.get("id", "")).strip()
    module = str(library.get("module", "")).strip()
    stability = str(library.get("stability", "")).strip()
    owner = str(library.get("owner", "")).strip()
    if not lid:
        issues.append(f"case {case_id}: library.id must be non-empty")
    if not module:
        issues.append(f"case {case_id}: library.module must be non-empty")
    if stability not in {"alpha", "beta", "stable", "internal"}:
        issues.append(
            f"case {case_id}: library.stability must be one of alpha|beta|stable|internal"
        )
    if not owner:
        issues.append(f"case {case_id}: library.owner must be non-empty")
    tags = library.get("tags")
    if tags is not None and (
        not isinstance(tags, list) or any(not isinstance(x, str) or not str(x).strip() for x in tags)
    ):
        issues.append(f"case {case_id}: library.tags must be list of non-empty strings when provided")

    harness = raw_case.get("harness")
    if not isinstance(harness, dict):
        return [*issues, f"case {case_id}: contract.export requires harness mapping"]
    exports = harness.get("exports")
    if not isinstance(exports, list) or not exports:
        return [*issues, f"case {case_id}: harness.exports must be a non-empty list"]

    for idx, raw_export in enumerate(exports):
        where = f"case {case_id}: harness.exports[{idx}]"
        if not isinstance(raw_export, dict):
            issues.append(f"{where} must be mapping")
            continue
        raw_as = str(raw_export.get("as", "")).strip()
        if not raw_as:
            issues.append(f"{where}.as must be non-empty")
            canonical_as = ""
        else:
            try:
                canonical_as = normalize_export_symbol(case_domain, raw_as)
            except ValueError as exc:
                issues.append(f"{where}: {exc}")
                canonical_as = ""
        if canonical_as:
            for prior_idx in range(idx):
                prior = exports[prior_idx]
                if not isinstance(prior, dict):
                    continue
                prior_as = str(prior.get("as", "")).strip()
                if not prior_as:
                    continue
                if normalize_export_symbol(case_domain, prior_as) == canonical_as:
                    issues.append(
                        f"{where}: canonical export symbol collision "
                        f"(raw_as={raw_as}, domain={case_domain or '<none>'}, canonical={canonical_as})"
                    )
                    break
        params = raw_export.get("params")
        if not isinstance(params, list) or any(not isinstance(x, str) or not str(x).strip() for x in params):
            issues.append(f"{where}.params must be list of non-empty strings")
            params = []
        else:
            params = [str(x).strip() for x in params]
        doc = raw_export.get("doc")
        if not isinstance(doc, dict):
            issues.append(f"{where}.doc must be mapping")
            continue
        unknown_doc = sorted(str(k) for k in doc.keys() if str(k) not in _LIBRARY_DOC_ALLOWED_KEYS)
        if unknown_doc:
            issues.append(f"{where}.doc has unsupported keys: {', '.join(unknown_doc)}")
        summary = str(doc.get("summary", "")).strip()
        description = str(doc.get("description", "")).strip()
        if not summary:
            issues.append(f"{where}.doc.summary must be non-empty")
        if not description:
            issues.append(f"{where}.doc.description must be non-empty")

        doc_params = doc.get("params")
        if not isinstance(doc_params, list) or not doc_params:
            issues.append(f"{where}.doc.params must be non-empty list")
        else:
            names: list[str] = []
            for pidx, item in enumerate(doc_params):
                pwhere = f"{where}.doc.params[{pidx}]"
                if not isinstance(item, dict):
                    issues.append(f"{pwhere} must be mapping")
                    continue
                name = str(item.get("name", "")).strip()
                ptype = str(item.get("type", "")).strip()
                pdesc = str(item.get("description", "")).strip()
                preq = item.get("required")
                if not name:
                    issues.append(f"{pwhere}.name must be non-empty")
                if not ptype:
                    issues.append(f"{pwhere}.type must be non-empty")
                if not pdesc:
                    issues.append(f"{pwhere}.description must be non-empty")
                if not isinstance(preq, bool):
                    issues.append(f"{pwhere}.required must be bool")
                names.append(name)
            if names != list(params):
                issues.append(f"{where}.doc.params names must match params exactly")

        returns = doc.get("returns")
        if not isinstance(returns, dict):
            issues.append(f"{where}.doc.returns must be mapping")
        else:
            if not str(returns.get("type", "")).strip():
                issues.append(f"{where}.doc.returns.type must be non-empty")
            if not str(returns.get("description", "")).strip():
                issues.append(f"{where}.doc.returns.description must be non-empty")

        errors = doc.get("errors")
        if not isinstance(errors, list) or not errors:
            issues.append(f"{where}.doc.errors must be non-empty list")
        else:
            for eidx, item in enumerate(errors):
                ewhere = f"{where}.doc.errors[{eidx}]"
                if not isinstance(item, dict):
                    issues.append(f"{ewhere} must be mapping")
                    continue
                if not str(item.get("code", "")).strip():
                    issues.append(f"{ewhere}.code must be non-empty")
                if not str(item.get("when", "")).strip():
                    issues.append(f"{ewhere}.when must be non-empty")
                category = str(item.get("category", "")).strip()
                if category not in {"schema", "assertion", "runtime"}:
                    issues.append(f"{ewhere}.category must be schema|assertion|runtime")

        examples = doc.get("examples")
        if not isinstance(examples, list) or not examples:
            issues.append(f"{where}.doc.examples must be non-empty list")
        else:
            for xidx, item in enumerate(examples):
                xwhere = f"{where}.doc.examples[{xidx}]"
                if not isinstance(item, dict):
                    issues.append(f"{xwhere} must be mapping")
                    continue
                if not str(item.get("title", "")).strip():
                    issues.append(f"{xwhere}.title must be non-empty")
                if item.get("input") is None:
                    issues.append(f"{xwhere}.input is required")
                if item.get("expected") is None:
                    issues.append(f"{xwhere}.expected is required")

        portability = doc.get("portability")
        if not isinstance(portability, dict):
            issues.append(f"{where}.doc.portability must be mapping")
        else:
            for key in ("python", "php", "rust"):
                if not isinstance(portability.get(key), bool):
                    issues.append(f"{where}.doc.portability.{key} must be bool")
        see_also = doc.get("see_also")
        if see_also is not None and (
            not isinstance(see_also, list)
            or any(not isinstance(x, str) or not str(x).strip() for x in see_also)
        ):
            issues.append(f"{where}.doc.see_also must be list of non-empty strings when provided")
        deprecated = doc.get("deprecated")
        if deprecated is not None:
            if not isinstance(deprecated, dict):
                issues.append(f"{where}.doc.deprecated must be mapping when provided")
            else:
                if not str(deprecated.get("replacement", "")).strip():
                    issues.append(f"{where}.doc.deprecated.replacement must be non-empty")
                if not str(deprecated.get("reason", "")).strip():
                    issues.append(f"{where}.doc.deprecated.reason must be non-empty")
    return issues


def _looks_like_assert_step_v1(item: Any) -> bool:
    return isinstance(item, dict) and "id" in item and "class" in item and "asserts" in item


def _normalize_step_assert_list(raw: Any, *, step_path: str) -> list[Any]:
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list) and raw:
        return list(raw)
    raise TypeError(f"{step_path}.assert must be a non-empty expression mapping or list")


def _normalize_imports(raw: Any, *, field_path: str) -> dict[str, dict[str, Any]]:
    if raw is None:
        return {}
    if not isinstance(raw, list):
        raise TypeError(f"{field_path} must be a list")
    out: dict[str, dict[str, Any]] = {}
    for idx, raw_item in enumerate(raw):
        if not isinstance(raw_item, dict):
            raise TypeError(f"{field_path}[{idx}] must be a mapping")
        src = str(raw_item.get("from", "")).strip()
        if src != "artifact":
            raise ValueError(f"{field_path}[{idx}].from must be artifact")
        raw_names = raw_item.get("names")
        if not isinstance(raw_names, list) or not raw_names:
            raise ValueError(f"{field_path}[{idx}].names must be a non-empty list")
        for name_idx, raw_name in enumerate(raw_names):
            source_name = str(raw_name).strip()
            if not source_name:
                raise ValueError(f"{field_path}[{idx}].names[{name_idx}] must be a non-empty string")
        raw_aliases = raw_item.get("as")
        aliases: dict[str, str] = {}
        if raw_aliases is not None:
            if not isinstance(raw_aliases, dict):
                raise TypeError(f"{field_path}[{idx}].as must be a mapping when provided")
            for raw_key, raw_val in raw_aliases.items():
                alias_from = str(raw_key).strip()
                alias_to = str(raw_val).strip()
                if not alias_from or not alias_to:
                    raise ValueError(f"{field_path}[{idx}].as keys and values must be non-empty strings")
                aliases[alias_from] = alias_to
            names_set = {str(name).strip() for name in raw_names}
            extra_alias_keys = sorted(k for k in aliases.keys() if k not in names_set)
            if extra_alias_keys:
                raise ValueError(
                    f"{field_path}[{idx}].as keys must be subset of names: {', '.join(extra_alias_keys)}"
                )
        unknown = sorted(set(str(k) for k in raw_item.keys()) - {"from", "names", "as"})
        if unknown:
            raise ValueError(f"{field_path}[{idx}] has unknown keys: {', '.join(unknown)}")
        for raw_name in raw_names:
            source_name = str(raw_name).strip()
            local_name = aliases.get(source_name, source_name)
            if local_name in out:
                raise ValueError(f"{field_path} defines duplicate local import symbol: {local_name}")
            out[local_name] = {"from": "artifact", "key": source_name}
    return out


def _lower_expect_steps(raw_expect: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_expect, dict):
        return []
    out: list[dict[str, Any]] = []
    if "violation_count" in raw_expect:
        out.append(
            {
                "class": "MUST",
                "imports": [
                    {
                        "from": "artifact",
                        "names": ["violation_count"],
                        "as": {"violation_count": "subject"},
                    }
                ],
                "assert": {
                    "std.logic.eq": [
                        {"var": "subject"},
                        {"lit": raw_expect.get("violation_count")},
                    ]
                },
            }
        )
    if "status" in raw_expect:
        out.append(
            {
                "class": "MUST",
                "imports": [
                    {
                        "from": "artifact",
                        "names": ["status"],
                        "as": {"status": "subject"},
                    }
                ],
                "assert": {
                    "std.logic.eq": [
                        {"var": "subject"},
                        {"lit": raw_expect.get("status")},
                    ]
                },
            }
        )
    summary = raw_expect.get("summary_json")
    if isinstance(summary, dict):
        for key, val in summary.items():
            out.append(
                {
                    "class": "MUST",
                    "imports": [
                        {
                            "from": "artifact",
                            "names": ["summary_json"],
                            "as": {"summary_json": "subject"},
                        }
                    ],
                    "assert": {
                        "std.logic.eq": [
                            {
                                "std.object.get_or": [
                                    {"var": "subject"},
                                    {"lit": str(key)},
                                    {"lit": None},
                                ]
                            },
                            {"lit": val},
                        ]
                    },
                }
            )
    return out


def _normalize_contract_steps(raw_assert: Any, *, raw_expect: Any, assert_path: str) -> list[dict[str, Any]]:
    # Canonical contract form: mapping with defaults + steps.
    if isinstance(raw_assert, dict):
        defaults_raw = raw_assert.get("defaults")
        defaults = defaults_raw if isinstance(defaults_raw, dict) else {}
        default_class = str(defaults.get("class", "MUST")).strip() or "MUST"
        if default_class not in {"MUST", "MAY", "MUST_NOT"}:
            raise ValueError(f"{assert_path}.defaults.class must be one of: MUST, MAY, MUST_NOT")
        if "target" in defaults or "on" in defaults:
            raise ValueError(f"{assert_path}.defaults.target/on is forbidden; use contract.imports")
        if "imports" in defaults:
            raise ValueError(f"{assert_path}.defaults.imports is forbidden; use {assert_path}.imports")
        root_imports_raw = raw_assert.get("imports")
        if isinstance(root_imports_raw, dict):
            if "defaults" in root_imports_raw:
                raise ValueError(f"{assert_path}.imports.defaults is forbidden; use {assert_path}.imports directly")
            if "steps" in root_imports_raw:
                raise ValueError(
                    f"{assert_path}.imports.steps is forbidden; use {assert_path}.steps[].imports"
                )
            raise ValueError(f"{assert_path}.imports must use list form: [{'{from, names, as?}'}]")
        default_imports = _normalize_imports(root_imports_raw, field_path=f"{assert_path}.imports")
        raw_steps = raw_assert.get("steps")
        if raw_steps is None:
            raw_steps = []
        if not isinstance(raw_steps, list):
            raise TypeError(f"{assert_path}.steps must be a list")
        synthetic = _lower_expect_steps(raw_expect)
        all_steps = list(raw_steps) + synthetic
        if not all_steps:
            return []
        out: list[dict[str, Any]] = []
        for idx, raw_step in enumerate(all_steps):
            if not isinstance(raw_step, dict):
                raise TypeError(f"{assert_path}.steps[{idx}] must be a mapping")
            step_class = str(raw_step.get("class", default_class)).strip() or default_class
            if step_class not in {"MUST", "MAY", "MUST_NOT"}:
                raise ValueError(f"{assert_path}.steps[{idx}].class must be one of: MUST, MAY, MUST_NOT")
            step_id = str(raw_step.get("id", "")).strip() or f"step_{idx + 1:03d}"
            if "target" in raw_step or "on" in raw_step:
                raise ValueError(f"{assert_path}.steps[{idx}].target/on is forbidden; use imports")
            if isinstance(raw_step.get("imports"), dict):
                raise ValueError(
                    f"{assert_path}.steps[{idx}].imports must use list form: [{'{from, names, as?}'}]"
                )
            step_imports = _normalize_imports(raw_step.get("imports"), field_path=f"{assert_path}.steps[{idx}].imports")
            merged_imports = dict(default_imports)
            merged_imports.update(step_imports)
            if "assert" not in raw_step:
                raise ValueError(f"{assert_path}.steps[{idx}].assert is required")
            checks = _normalize_step_assert_list(raw_step.get("assert"), step_path=f"{assert_path}.steps[{idx}]")
            out.append({"id": step_id, "class": step_class, "imports": merged_imports, "asserts": checks})
        return out

    # Accept v1 only for migration tooling compatibility.
    if isinstance(raw_assert, list):
        if not raw_assert:
            return []
        if not all(_looks_like_assert_step_v1(x) for x in raw_assert):
            raise ValueError("contract must use canonical form (mapping with defaults/steps)")
        return list(cast(list[dict[str, Any]], raw_assert))

    if raw_assert is None:
        synthetic = _lower_expect_steps(raw_expect)
        return _normalize_contract_steps(
            {"defaults": {"class": "MUST"}, "steps": synthetic},
            raw_expect=None,
            assert_path=assert_path,
        )
    raise TypeError("contract must be a mapping")


def compile_assert_tree(
    raw_assert: Any,
    *,
    raw_expect: Any = None,
    type_name: str,
    inherited_target: str | None = None,
    assert_path: str = "contract",
    strict_steps: bool = True,
) -> InternalAssertNode:
    normalized_steps = _normalize_contract_steps(raw_assert, raw_expect=raw_expect, assert_path=assert_path)
    if not normalized_steps:
        return GroupNode(op="MUST", target=inherited_target, children=[], assert_path=assert_path)

    seen_ids: set[str] = set()
    step_nodes: list[InternalAssertNode] = []
    for idx, raw_step in enumerate(normalized_steps):
        assert isinstance(raw_step, dict)
        step_id = str(raw_step.get("id", "")).strip()
        if not step_id:
            raise ValueError(f"{assert_path}.steps[{idx}].id must be a non-empty string")
        if step_id in seen_ids:
            raise ValueError(f"{assert_path} has duplicate step id: {step_id}")
        seen_ids.add(step_id)
        class_name = str(raw_step.get("class", "")).strip()
        if class_name not in {"MUST", "MAY", "MUST_NOT"}:
            raise ValueError(f"{assert_path}.steps[{idx}].class must be one of: MUST, MAY, MUST_NOT")
        step_imports = raw_step.get("imports")
        if not isinstance(step_imports, dict):
            raise TypeError(f"{assert_path}.steps[{idx}].imports must be a mapping")
        raw_checks = raw_step.get("asserts")
        if not isinstance(raw_checks, list) or not raw_checks:
            raise TypeError(f"{assert_path}.steps[{idx}].assert must be a non-empty mapping or list")
        children: list[InternalAssertNode] = [
            _compile_assert_expr_leaf(
                check,
                target=None,
                imports=dict(step_imports),
                assert_path=f"{assert_path}.steps[{idx}].assert[{cidx}]",
            )
            for cidx, check in enumerate(raw_checks)
        ]
        step_nodes.append(
            GroupNode(
                op=cast(Literal["MUST", "MAY", "MUST_NOT"], class_name),
                target=None,
                children=children,
                assert_path=f"{assert_path}.steps[{idx}]<{step_id}>",
            )
        )
    return GroupNode(op="MUST", target=inherited_target, children=step_nodes, assert_path=assert_path)


def compile_external_case(raw_case: dict[str, Any], *, doc_path: Path) -> InternalSpecCase:
    if not isinstance(raw_case, dict):
        raise TypeError("spec case must be a mapping")
    case_id = str(raw_case.get("id", "")).strip()
    type_name = str(raw_case.get("type", "")).strip()
    if not case_id:
        raise ValueError("spec case must include non-empty id")
    if not type_name:
        raise ValueError("spec case must include non-empty type")

    diagnostics = validate_case_shape(raw_case, type_name, doc_path.as_posix())
    if diagnostics:
        raise ValueError("; ".join(d.render() for d in diagnostics))

    harness = raw_case.get("harness")
    if harness is None:
        harness_map: dict[str, Any] = {}
    elif isinstance(harness, dict):
        harness_map = {str(k): v for k, v in harness.items()}
    else:
        raise TypeError("harness must be a mapping")

    assert_tree: InternalAssertNode
    producer_export_type = type_name in {"contract.export"}
    if producer_export_type:
        export_doc_issues = _validate_contract_export_docs(raw_case)
        if export_doc_issues:
            raise ValueError("; ".join(export_doc_issues))
        # Producer-only case type: exported callables are compiled from raw
        # contract step asserts via chain_engine, not from runtime assertion targets.
        assert_tree = GroupNode(op="MUST", target=None, children=[], assert_path="contract")
    else:
        assert_tree = compile_assert_tree(
            raw_case.get("contract"),
            raw_expect=raw_case.get("expect"),
            type_name=type_name,
            strict_steps=True,
        )

    metadata = {
        "expect": raw_case.get("expect"),
        "requires": raw_case.get("requires"),
        "assert_health": raw_case.get("assert_health"),
        "source": {"doc_path": doc_path.as_posix()},
    }

    title_raw = raw_case.get("title")
    title = None if title_raw is None else str(title_raw)

    return InternalSpecCase(
        id=case_id,
        type=type_name,
        title=title,
        doc_path=doc_path,
        harness=harness_map,
        metadata=metadata,
        raw_case=dict(raw_case),
        assert_tree=assert_tree,
    )
