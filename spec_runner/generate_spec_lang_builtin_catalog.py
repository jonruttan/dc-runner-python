#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

import yaml

from spec_runner.docs_generators import parse_generated_block, replace_generated_block, write_json
from spec_runner.docs_template_engine import render_moustache
from spec_runner.spec_lang import _builtin_arity_table
from spec_runner.spec_lang_std_names import FLAT_TO_STD
from spec_runner.spec_lang_stdlib_profile import SPECIAL_FORMS


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return repo_root / str(raw).lstrip("/")


def _php_builtin_symbols(php_text: str) -> set[str]:
    out: set[str] = set()
    for m in re.finditer(r"\$op === '([a-z0-9_.]+)'", php_text):
        out.add(FLAT_TO_STD.get(m.group(1), m.group(1)))
    for form in SPECIAL_FORMS:
        out.add(form)
    return out


def _python_symbols() -> set[str]:
    out = set(_builtin_arity_table().keys())
    out.update(SPECIAL_FORMS)
    return out


def _namespace_for(symbol: str) -> str:
    if symbol in SPECIAL_FORMS:
        return "core"
    if not symbol.startswith("std."):
        return "core"
    parts = symbol.split(".")
    return parts[1] if len(parts) > 1 else "core"


def _default_summary(symbol: str, arity: int | None) -> str:
    if symbol == "std.core.subject":
        return "Returns the current assertion subject value."
    if symbol in SPECIAL_FORMS:
        return f"Spec-lang special form `{symbol}` for expression control and binding."
    suffix = symbol.split(".")[-1]
    if arity is None:
        return f"Evaluates `{suffix}` with runtime-defined argument shape."
    return f"Evaluates `{suffix}` with arity {arity}."


def _default_params(arity: int | None) -> list[dict[str, Any]]:
    if arity is None:
        return [
            {
                "name": "args",
                "type": "list",
                "description": "Operator-defined argument list.",
                "required": True,
            }
        ]
    out: list[dict[str, Any]] = []
    for i in range(arity):
        out.append(
            {
                "name": f"arg{i + 1}",
                "type": "json",
                "description": f"Positional argument {i + 1}.",
                "required": True,
            }
        )
    return out


def _default_returns(symbol: str) -> dict[str, Any]:
    ns = _namespace_for(symbol)
    if ns in {"logic", "type", "set"}:
        rtype = "bool"
    elif ns in {"math"}:
        rtype = "number"
    elif ns in {"string"}:
        rtype = "string"
    elif ns in {"collection"}:
        rtype = "json"
    else:
        rtype = "json"
    return {"type": rtype, "description": "Deterministic pure return value."}


def _default_errors() -> list[dict[str, str]]:
    return [
        {
            "category": "schema",
            "condition": "Unknown symbol, arity mismatch, or invalid argument types.",
        }
    ]


def _default_examples(symbol: str, arity: int | None) -> list[dict[str, str]]:
    if symbol == "std.core.subject":
        expr = "std.core.subject"
    elif arity is None:
        expr = f"{symbol}(...)"
    else:
        args = ", ".join(f"arg{i + 1}" for i in range(arity))
        expr = f"{symbol}({args})"
    return [
        {
            "title": "Basic usage",
            "expr": expr,
            "result": "Deterministic result per symbol contract.",
        }
    ]


def _clean_params(raw: Any, arity: int | None) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        return _default_params(arity)
    out: list[dict[str, Any]] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip() or f"arg{i + 1}"
        ptype = str(item.get("type", "json")).strip() or "json"
        desc = str(item.get("description", "")).strip() or f"Argument {i + 1}."
        required = bool(item.get("required", True))
        out.append({"name": name, "type": ptype, "description": desc, "required": required})
    return out or _default_params(arity)


def _clean_examples(raw: Any, symbol: str, arity: int | None) -> list[dict[str, str]]:
    if not isinstance(raw, list) or not raw:
        return _default_examples(symbol, arity)
    out: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip() or "Example"
        expr = str(item.get("expr", "")).strip() or symbol
        result = str(item.get("result", "")).strip() or "Deterministic output."
        out.append({"title": title, "expr": expr, "result": result})
    return out or _default_examples(symbol, arity)


def _chapter_name(ns: str) -> str:
    mapping = {
        "core": "93a_std_core.md",
        "logic": "93b_std_logic.md",
        "math": "93c_std_math.md",
        "string": "93d_std_string.md",
        "collection": "93e_std_collection.md",
        "object": "93f_std_object.md",
        "type": "93g_std_type.md",
        "set": "93h_std_set.md",
        "json_schema_fn_null": "93i_std_json_schema_fn_null.md",
    }
    return mapping[ns]


def _namespace_bucket(symbol: str) -> str:
    ns = _namespace_for(symbol)
    if ns in {"json", "schema", "fn", "null"}:
        return "json_schema_fn_null"
    return ns if ns in {"core", "logic", "math", "string", "collection", "object", "type", "set"} else "core"


def _build_payload(repo_root: Path) -> dict[str, Any]:
    profile_path = repo_root / "specs/schema/spec_lang_stdlib_profile_v1.yaml"
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    symbols_meta = profile.get("symbols") if isinstance(profile, dict) else None
    if not isinstance(symbols_meta, dict):
        raise ValueError("spec_lang_stdlib_profile_v1.yaml: symbols must be a mapping")

    py_syms = _python_symbols()
    php_text = (repo_root / "runners/php/spec_runner.php").read_text(encoding="utf-8")
    php_syms = _php_builtin_symbols(php_text)

    builtins: list[dict[str, Any]] = []
    missing_docs = 0
    for symbol in sorted(symbols_meta.keys()):
        meta = symbols_meta[symbol] if isinstance(symbols_meta[symbol], dict) else {}
        arity_raw = meta.get("arity")
        arity = int(arity_raw) if isinstance(arity_raw, int) else None
        summary = str(meta.get("summary", "")).strip() or _default_summary(symbol, arity)
        details = str(meta.get("details", "")).strip()
        params = _clean_params(meta.get("params"), arity)
        returns_raw = meta.get("returns")
        returns_map: dict[str, Any] = returns_raw if isinstance(returns_raw, dict) else _default_returns(symbol)
        returns = {
            "type": str(returns_map.get("type", "json")).strip() or "json",
            "description": str(returns_map.get("description", "")).strip() or "Deterministic pure return value.",
        }
        errors_raw = meta.get("errors")
        errors: list[dict[str, Any]] = errors_raw if isinstance(errors_raw, list) else _default_errors()
        cleaned_errors: list[dict[str, str]] = []
        for e in errors:
            if isinstance(e, dict):
                cleaned_errors.append(
                    {
                        "category": str(e.get("category", "schema")).strip() or "schema",
                        "condition": str(e.get("condition", "Invalid usage.")).strip() or "Invalid usage.",
                    }
                )
        if not cleaned_errors:
            cleaned_errors = _default_errors()
        examples = _clean_examples(meta.get("examples"), symbol, arity)
        tags_raw = meta.get("tags")
        tags: list[Any] = tags_raw if isinstance(tags_raw, list) else ["pure", "deterministic"]
        tags = [str(x).strip() for x in tags if str(x).strip()]
        since = str(meta.get("since", "v1")).strip() or "v1"
        deprecated = meta.get("deprecated") if isinstance(meta.get("deprecated"), dict) else None
        if deprecated is not None:
            deprecated = {
                "in": str(deprecated.get("in", "")).strip(),
                "replacement": str(deprecated.get("replacement", "")).strip(),
                "note": str(deprecated.get("note", "")).strip(),
            }

        if (
            not summary
            or not isinstance(params, list)
            or not params
            or not isinstance(returns, dict)
            or not str(returns.get("description", "")).strip()
            or not isinstance(cleaned_errors, list)
            or not cleaned_errors
            or not isinstance(examples, list)
            or not examples
        ):
            missing_docs += 1

        bucket = _namespace_bucket(symbol)
        builtins.append(
            {
                "symbol": symbol,
                "namespace": bucket,
                "category": str(meta.get("category", _namespace_for(symbol))).strip() or _namespace_for(symbol),
                "arity": arity,
                "signature": f"{symbol}/{arity if arity is not None else 'var'}",
                "summary": summary,
                "details": details,
                "params": params,
                "returns": returns,
                "errors": cleaned_errors,
                "examples": examples,
                "tags": tags,
                "since": since,
                "deprecated": deprecated,
                "python_supported": symbol in py_syms,
                "php_supported": symbol in php_syms,
                "parity": symbol in py_syms and symbol in php_syms,
                "anchor": symbol.replace(".", "-"),
            }
        )

    namespaces: dict[str, dict[str, Any]] = {
        "core": {"title": "Core & Special Forms", "chapter": _chapter_name("core"), "symbols": []},
        "logic": {"title": "Logic", "chapter": _chapter_name("logic"), "symbols": []},
        "math": {"title": "Math", "chapter": _chapter_name("math"), "symbols": []},
        "string": {"title": "String", "chapter": _chapter_name("string"), "symbols": []},
        "collection": {"title": "Collection", "chapter": _chapter_name("collection"), "symbols": []},
        "object": {"title": "Object", "chapter": _chapter_name("object"), "symbols": []},
        "type": {"title": "Type", "chapter": _chapter_name("type"), "symbols": []},
        "set": {"title": "Set", "chapter": _chapter_name("set"), "symbols": []},
        "json_schema_fn_null": {
            "title": "JSON / Schema / Functional / Null",
            "chapter": _chapter_name("json_schema_fn_null"),
            "symbols": [],
        },
    }

    for entry in builtins:
        namespaces[entry["namespace"]]["symbols"].append(entry)

    quality = {
        "missing_doc_symbol_count": missing_docs,
        "coverage_ratio": 0.0 if not builtins else (len(builtins) - missing_docs) / len(builtins),
    }

    payload: dict[str, Any] = {
        "version": 2,
        "summary": {
            "builtin_count": len(builtins),
            "parity_count": sum(1 for x in builtins if bool(x.get("parity"))),
            "all_parity": all(bool(x.get("parity")) for x in builtins),
            "namespace_count": len(namespaces),
        },
        "quality": quality,
        "chapters": [
            {"key": key, "title": value["title"], "path": f"/docs/book/{value['chapter']}", "symbol_count": len(value["symbols"])}
            for key, value in namespaces.items()
        ],
        "namespaces": namespaces,
        "builtins": builtins,
    }
    score = float(quality["coverage_ratio"])
    quality["score"] = round(score, 4)
    return payload


def _render_index_md(payload: dict[str, Any], *, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    return render_moustache(template, {"stdlib": payload}, strict=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate spec-lang builtin reference catalog JSON and appendix index section.")
    ap.add_argument("--out", default=".artifacts/spec-lang-builtin-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/93_appendix_spec_lang_builtin_catalog.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _build_payload(repo_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    md_block = _render_index_md(
        payload,
        template_path=repo_root / "docs/book/templates/spec_lang_builtin_catalog_template.md",
    )
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="spec_lang_builtin_catalog",
        body=md_block,
    )

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        if parse_generated_block(doc_path.read_text(encoding="utf-8"), surface_id="spec_lang_builtin_catalog").strip() != md_block.strip():
            print(f"{ns.doc_out}: generated content out of date")
            return 1
        if out_path.exists() and out_path.read_text(encoding="utf-8") != expected_json:
            print(f"{ns.out}: generated content out of date")
            return 1
        return 0

    write_json(out_path, payload)
    doc_path.write_text(updated_doc, encoding="utf-8")
    print(f"wrote {ns.out}")
    print(f"wrote {ns.doc_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
