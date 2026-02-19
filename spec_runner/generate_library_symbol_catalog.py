#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from spec_runner.codecs import load_external_cases
from spec_runner.docs_generators import parse_generated_block, replace_generated_block, write_json
from spec_runner.docs_template_engine import render_moustache
from spec_runner.spec_domain import normalize_case_domain, normalize_export_symbol

_STABILITY = {"alpha", "beta", "stable", "internal"}
_ERROR_CATEGORY = {"schema", "assertion", "runtime"}
_DOC_ALLOWED_KEYS = {
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


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return repo_root / str(raw).lstrip("/")


def _as_non_empty_string(value: Any, *, field: str, issues: list[str], where: str) -> str:
    out = str(value or "").strip()
    if not out:
        issues.append(f"{where}: {field} must be a non-empty string")
    return out


def _validate_library_block(
    *,
    raw_library: Any,
    issues: list[str],
    where: str,
) -> dict[str, Any]:
    if not isinstance(raw_library, dict):
        issues.append(f"{where}: library must be a mapping")
        return {}
    out: dict[str, Any] = {
        "id": _as_non_empty_string(raw_library.get("id"), field="library.id", issues=issues, where=where),
        "module": _as_non_empty_string(
            raw_library.get("module"),
            field="library.module",
            issues=issues,
            where=where,
        ),
        "stability": _as_non_empty_string(
            raw_library.get("stability"),
            field="library.stability",
            issues=issues,
            where=where,
        ),
        "owner": _as_non_empty_string(
            raw_library.get("owner"),
            field="library.owner",
            issues=issues,
            where=where,
        ),
    }
    if out.get("stability") and out["stability"] not in _STABILITY:
        issues.append(
            f"{where}: library.stability must be one of alpha|beta|stable|internal"
        )
    tags = raw_library.get("tags")
    if tags is None:
        out["tags"] = []
    elif isinstance(tags, list) and all(isinstance(x, str) and x.strip() for x in tags):
        out["tags"] = [str(x).strip() for x in tags]
    else:
        issues.append(f"{where}: library.tags must be a list of non-empty strings when provided")
        out["tags"] = []
    return out


def _clean_doc_params(
    *,
    raw: Any,
    export_params: list[str],
    issues: list[str],
    where: str,
) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        issues.append(f"{where}: doc.params must be a non-empty list")
        return []
    out: list[dict[str, Any]] = []
    for idx, item in enumerate(raw):
        item_where = f"{where}.params[{idx}]"
        if not isinstance(item, dict):
            issues.append(f"{item_where}: must be a mapping")
            continue
        name = _as_non_empty_string(item.get("name"), field="name", issues=issues, where=item_where)
        ptype = _as_non_empty_string(item.get("type"), field="type", issues=issues, where=item_where)
        desc = _as_non_empty_string(
            item.get("description"),
            field="description",
            issues=issues,
            where=item_where,
        )
        required = item.get("required")
        if not isinstance(required, bool):
            issues.append(f"{item_where}: required must be bool")
            required = True
        row: dict[str, Any] = {
            "name": name,
            "type": ptype,
            "description": desc,
            "required": required,
            "default": item.get("default"),
        }
        out.append(row)
    param_names = [x.get("name", "") for x in out]
    if param_names != export_params:
        issues.append(
            f"{where}: doc.params names must exactly match harness.exports[].params order"
        )
    return out


def _clean_doc_errors(*, raw: Any, issues: list[str], where: str) -> list[dict[str, str]]:
    if not isinstance(raw, list) or not raw:
        issues.append(f"{where}: doc.errors must be a non-empty list")
        return []
    out: list[dict[str, str]] = []
    for idx, item in enumerate(raw):
        item_where = f"{where}.errors[{idx}]"
        if not isinstance(item, dict):
            issues.append(f"{item_where}: must be a mapping")
            continue
        code = _as_non_empty_string(item.get("code"), field="code", issues=issues, where=item_where)
        when = _as_non_empty_string(item.get("when"), field="when", issues=issues, where=item_where)
        category = _as_non_empty_string(
            item.get("category"),
            field="category",
            issues=issues,
            where=item_where,
        )
        if category and category not in _ERROR_CATEGORY:
            issues.append(f"{item_where}: category must be schema|assertion|runtime")
        out.append({"code": code, "when": when, "category": category})
    return out


def _clean_doc_examples(*, raw: Any, issues: list[str], where: str) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        issues.append(f"{where}: doc.examples must be a non-empty list")
        return []
    out: list[dict[str, Any]] = []
    for idx, item in enumerate(raw):
        item_where = f"{where}.examples[{idx}]"
        if not isinstance(item, dict):
            issues.append(f"{item_where}: must be a mapping")
            continue
        title = _as_non_empty_string(item.get("title"), field="title", issues=issues, where=item_where)
        row = {
            "title": title,
            "input": item.get("input"),
            "expected": item.get("expected"),
            "notes": None if item.get("notes") is None else str(item.get("notes")),
        }
        if row["input"] is None:
            issues.append(f"{item_where}: input is required")
        if row["expected"] is None:
            issues.append(f"{item_where}: expected is required")
        out.append(row)
    return out


def _clean_doc_portability(*, raw: Any, issues: list[str], where: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        issues.append(f"{where}: doc.portability must be a mapping")
        return {"python": False, "php": False, "rust": False, "notes": ""}
    out = {}
    for key in ("python", "php", "rust"):
        value = raw.get(key)
        if not isinstance(value, bool):
            issues.append(f"{where}: doc.portability.{key} must be bool")
            value = False
        out[key] = value
    notes = raw.get("notes")
    out["notes"] = "" if notes is None else str(notes).strip()
    return out


def _anchor_for(symbol: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", symbol.lower()).strip("_")
    return f"symbol-{slug}" if slug else "symbol"


def _build_payload(repo_root: Path, *, libs_root: Path) -> dict[str, Any]:
    issues: list[str] = []
    symbols: list[dict[str, Any]] = []
    modules: dict[str, dict[str, Any]] = {}

    for doc_path, case in load_external_cases(libs_root, formats={"md"}, md_pattern="*.spec.md"):
        if str(case.get("type", "")).strip() != "contract.export":
            continue
        case_id = str(case.get("id", "")).strip() or "<unknown>"
        rel = "/" + doc_path.resolve().relative_to(repo_root.resolve()).as_posix()
        where = f"{rel}: case {case_id}"
        try:
            case_domain = normalize_case_domain(case.get("domain"))
        except (TypeError, ValueError):
            issues.append(f"{where}: domain must be a non-empty string when provided")
            case_domain = None
        library = _validate_library_block(raw_library=case.get("library"), issues=issues, where=where)

        harness = case.get("harness")
        if not isinstance(harness, dict):
            issues.append(f"{where}: harness must be mapping for contract.export")
            continue
        exports = harness.get("exports")
        if not isinstance(exports, list) or not exports:
            issues.append(f"{where}: harness.exports must be a non-empty list")
            continue

        for exp_idx, exp in enumerate(exports):
            exp_where = f"{where}.harness.exports[{exp_idx}]"
            if not isinstance(exp, dict):
                issues.append(f"{exp_where}: must be a mapping")
                continue
            raw_symbol = _as_non_empty_string(exp.get("as"), field="as", issues=issues, where=exp_where)
            symbol = normalize_export_symbol(case_domain, raw_symbol) if raw_symbol else ""
            export_from = _as_non_empty_string(exp.get("from"), field="from", issues=issues, where=exp_where)
            export_path = _as_non_empty_string(exp.get("path"), field="path", issues=issues, where=exp_where)
            if export_from and export_from != "assert.function":
                issues.append(f"{exp_where}: from must be assert.function")
            raw_params = exp.get("params")
            if not isinstance(raw_params, list) or not all(isinstance(x, str) and x.strip() for x in raw_params):
                issues.append(f"{exp_where}: params must be a list of non-empty strings")
                export_params: list[str] = []
            else:
                export_params = [str(x).strip() for x in raw_params]

            doc = exp.get("doc")
            if not isinstance(doc, dict):
                issues.append(f"{exp_where}: doc must be a mapping")
                continue
            unknown_doc_keys = sorted(str(k) for k in doc.keys() if str(k) not in _DOC_ALLOWED_KEYS)
            if unknown_doc_keys:
                issues.append(f"{exp_where}: unsupported doc keys: {', '.join(unknown_doc_keys)}")
            summary = _as_non_empty_string(
                doc.get("summary"),
                field="doc.summary",
                issues=issues,
                where=exp_where,
            )
            description = _as_non_empty_string(
                doc.get("description"),
                field="doc.description",
                issues=issues,
                where=exp_where,
            )
            params = _clean_doc_params(
                raw=doc.get("params"),
                export_params=export_params,
                issues=issues,
                where=exp_where,
            )
            returns_raw = doc.get("returns")
            if not isinstance(returns_raw, dict):
                issues.append(f"{exp_where}: doc.returns must be a mapping")
                returns = {"type": "", "description": ""}
            else:
                returns = {
                    "type": _as_non_empty_string(
                        returns_raw.get("type"),
                        field="doc.returns.type",
                        issues=issues,
                        where=exp_where,
                    ),
                    "description": _as_non_empty_string(
                        returns_raw.get("description"),
                        field="doc.returns.description",
                        issues=issues,
                        where=exp_where,
                    ),
                }
            errors = _clean_doc_errors(raw=doc.get("errors"), issues=issues, where=exp_where)
            examples = _clean_doc_examples(raw=doc.get("examples"), issues=issues, where=exp_where)
            portability = _clean_doc_portability(
                raw=doc.get("portability"),
                issues=issues,
                where=exp_where,
            )
            see_also_raw = doc.get("see_also")
            if see_also_raw is None:
                see_also: list[str] = []
            elif isinstance(see_also_raw, list) and all(isinstance(x, str) and x.strip() for x in see_also_raw):
                see_also = [str(x).strip() for x in see_also_raw]
            else:
                issues.append(f"{exp_where}: doc.see_also must be a list of non-empty strings when provided")
                see_also = []
            since_raw = str(doc.get("since", "v1")).strip() or "v1"
            deprecated_raw = doc.get("deprecated")
            deprecated = None
            if deprecated_raw is not None:
                if not isinstance(deprecated_raw, dict):
                    issues.append(f"{exp_where}: doc.deprecated must be a mapping when provided")
                else:
                    deprecated = {
                        "replacement": _as_non_empty_string(
                            deprecated_raw.get("replacement"),
                            field="doc.deprecated.replacement",
                            issues=issues,
                            where=exp_where,
                        ),
                        "reason": _as_non_empty_string(
                            deprecated_raw.get("reason"),
                            field="doc.deprecated.reason",
                            issues=issues,
                            where=exp_where,
                        ),
                    }

            if not symbol:
                continue
            signature = f"{symbol}({', '.join(export_params)})"
            row: dict[str, Any] = {
                "symbol": symbol,
                "signature": signature,
                "summary": summary,
                "description": description,
                "params": params,
                "returns": returns,
                "errors": errors,
                "examples": examples,
                "portability": portability,
                "see_also": see_also,
                "since": since_raw,
                "deprecated": deprecated,
                "source_doc": rel,
                "case_id": case_id,
                "export_path": export_path,
                "contract_badge": f"Contract-backed: `{rel}#{case_id}` via `{export_path}`",
                "library_id": str(library.get("id", "")),
                "module": str(library.get("module", "")),
                "stability": str(library.get("stability", "")),
                "owner": str(library.get("owner", "")),
                "tags": list(library.get("tags", [])),
                "anchor": _anchor_for(symbol),
            }
            symbols.append(row)
            module_key = str(row.get("module", "")).strip() or "unknown"
            mod = modules.setdefault(
                module_key,
                {"module": module_key, "library_ids": set(), "symbol_count": 0, "symbols": []},
            )
            mod["symbol_count"] = int(mod["symbol_count"]) + 1
            if row.get("library_id"):
                mod["library_ids"].add(str(row["library_id"]))
            mod["symbols"].append(symbol)

    if issues:
        preview = "\n".join(issues[:200])
        raise ValueError(preview)

    symbols_sorted = sorted(symbols, key=lambda x: (str(x.get("module", "")), str(x.get("symbol", ""))))
    module_rows: list[dict[str, Any]] = []
    for key in sorted(modules.keys()):
        mod = modules[key]
        module_rows.append(
            {
                "module": key,
                "symbol_count": int(mod.get("symbol_count", 0)),
                "library_ids": sorted(str(x) for x in (mod.get("library_ids") or set())),
                "symbols": sorted(str(x) for x in (mod.get("symbols") or [])),
                "anchor": _anchor_for(key),
            }
        )

    return {
        "version": 1,
        "summary": {
            "module_count": len(module_rows),
            "symbol_count": len(symbols_sorted),
            "library_root": "/" + libs_root.resolve().relative_to(repo_root.resolve()).as_posix(),
        },
        "modules": module_rows,
        "symbols": symbols_sorted,
    }


def _render_md(payload: dict[str, Any], *, template_path: Path, key: str) -> str:
    template = template_path.read_text(encoding="utf-8")
    return render_moustache(template, {key: payload}, strict=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Generate library symbol reference catalog and markdown reference pages."
    )
    ap.add_argument("--cases", default="specs/libraries")
    ap.add_argument("--out", default=".artifacts/library-symbol-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/93j_library_symbol_reference.md")
    ap.add_argument("--index-out", default="docs/book/93k_library_symbol_index.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    libs_root = _resolve_cli_path(repo_root, str(ns.cases))
    payload = _build_payload(repo_root, libs_root=libs_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    index_path = _resolve_cli_path(repo_root, str(ns.index_out))
    ref_block = _render_md(
        payload,
        template_path=repo_root / "docs/book/templates/library_symbol_reference_template.md",
        key="catalog",
    )
    index_block = _render_md(
        payload,
        template_path=repo_root / "docs/book/templates/library_symbol_index_template.md",
        key="catalog",
    )
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="library_symbol_reference",
        body=ref_block,
    )
    updated_index = replace_generated_block(
        index_path.read_text(encoding="utf-8"),
        surface_id="library_symbol_index",
        body=index_block,
    )

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        if parse_generated_block(
            doc_path.read_text(encoding="utf-8"),
            surface_id="library_symbol_reference",
        ).strip() != ref_block.strip():
            print(f"{ns.doc_out}: generated content out of date")
            return 1
        if parse_generated_block(
            index_path.read_text(encoding="utf-8"),
            surface_id="library_symbol_index",
        ).strip() != index_block.strip():
            print(f"{ns.index_out}: generated content out of date")
            return 1
        if out_path.exists() and out_path.read_text(encoding="utf-8") != expected_json:
            print(f"{ns.out}: generated content out of date")
            return 1
        return 0

    write_json(out_path, payload)
    doc_path.write_text(updated_doc, encoding="utf-8")
    index_path.write_text(updated_index, encoding="utf-8")
    print(f"wrote {ns.out}")
    print(f"wrote {ns.doc_out}")
    print(f"wrote {ns.index_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
