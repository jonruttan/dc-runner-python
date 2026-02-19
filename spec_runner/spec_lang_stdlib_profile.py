from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from spec_runner.spec_lang import _builtin_arity_table
from spec_runner.spec_lang_std_names import FLAT_TO_STD


PROFILE_PATH = "specs/schema/spec_lang_stdlib_profile_v1.yaml"
DOC_SYNC_FILES = (
    "specs/contract/03b_spec_lang_v1.md",
    "specs/schema/schema_v1.md",
    "docs/book/90_reference_guide.md",
)
DOC_SYNC_REQUIRED_TOKENS = (
    "spec_lang_stdlib_profile_v1.yaml",
    "19_spec_lang_stdlib_profile_v1.md",
)
SPECIAL_FORMS = {"if", "let", "fn", "call", "var"}


def load_stdlib_profile(repo_root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = repo_root / PROFILE_PATH
    if not path.exists():
        return None, [f"{PROFILE_PATH}:1: missing stdlib profile"]
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None, [f"{PROFILE_PATH}:1: stdlib profile must be a mapping"]
    return payload, []


def _extract_profile_symbols(profile: dict[str, Any]) -> tuple[dict[str, int | None], list[str]]:
    symbols = profile.get("symbols")
    if not isinstance(symbols, dict) or not symbols:
        return {}, [f"{PROFILE_PATH}:1: symbols must be a non-empty mapping"]
    out: dict[str, int | None] = {}
    errs: list[str] = []
    for name, meta in sorted(symbols.items()):
        sym = str(name).strip()
        if not sym:
            errs.append(f"{PROFILE_PATH}:1: symbol names must be non-empty")
            continue
        if not isinstance(meta, dict):
            errs.append(f"{PROFILE_PATH}:1: symbols.{sym} must be a mapping")
            continue
        arity = meta.get("arity")
        if arity is None:
            out[sym] = None
        elif isinstance(arity, int) and arity >= 0:
            out[sym] = int(arity)
        else:
            errs.append(f"{PROFILE_PATH}:1: symbols.{sym}.arity must be int >= 0 or null")
    return out, errs


def _python_surface() -> dict[str, int | None]:
    table = _builtin_arity_table()
    out: dict[str, int | None] = {k: int(v) for k, v in table.items()}
    for sym in SPECIAL_FORMS:
        out[sym] = None
    return out


def _php_surface(repo_root: Path) -> dict[str, int | None]:
    php_file = repo_root / "runners/php/spec_runner.php"
    if not php_file.exists():
        return {}
    raw = php_file.read_text(encoding="utf-8")
    flat_ops = set(re.findall(r"\$op === '([a-z0-9_.]+)'", raw))
    out: dict[str, int | None] = {}
    for sym in sorted(flat_ops):
        out[FLAT_TO_STD.get(sym, sym)] = None
    for sym in SPECIAL_FORMS:
        out[sym] = None
    return out


def spec_lang_stdlib_report_jsonable(repo_root: Path) -> dict[str, Any]:
    profile, errs = load_stdlib_profile(repo_root)
    if profile is None:
        return {
            "version": 1,
            "summary": {
                "profile_symbol_count": 0,
                "python_symbol_count": 0,
                "php_symbol_count": 0,
                "missing_in_python_count": 0,
                "missing_in_php_count": 0,
                "arity_mismatch_count": 0,
                "docs_sync_missing_count": 0,
            },
            "errors": errs,
        }
    profile_symbols, profile_errs = _extract_profile_symbols(profile)
    python_surface = _python_surface()
    php_surface = _php_surface(repo_root)

    missing_python = sorted(sym for sym in profile_symbols if sym not in python_surface)
    missing_php = sorted(sym for sym in profile_symbols if sym not in php_surface)
    arity_mismatch: list[str] = []
    for sym, arity in profile_symbols.items():
        if arity is None:
            continue
        py_arity = python_surface.get(sym)
        if py_arity is None:
            continue
        if py_arity != arity:
            arity_mismatch.append(f"{sym}: profile={arity} python={py_arity}")

    docs_sync_missing: list[str] = []
    for rel in DOC_SYNC_FILES:
        p = repo_root / rel
        if not p.exists():
            docs_sync_missing.append(f"{rel}: missing")
            continue
        raw = p.read_text(encoding="utf-8")
        for tok in DOC_SYNC_REQUIRED_TOKENS:
            if tok not in raw:
                docs_sync_missing.append(f"{rel}: missing token {tok}")

    errors = [*errs, *profile_errs]
    return {
        "version": 1,
        "summary": {
            "profile_symbol_count": len(profile_symbols),
            "python_symbol_count": len(python_surface),
            "php_symbol_count": len(php_surface),
            "missing_in_python_count": len(missing_python),
            "missing_in_php_count": len(missing_php),
            "arity_mismatch_count": len(arity_mismatch),
            "docs_sync_missing_count": len(docs_sync_missing),
        },
        "profile_symbols": profile_symbols,
        "python_symbols": sorted(python_surface),
        "php_symbols": sorted(php_surface),
        "missing_in_python": missing_python,
        "missing_in_php": missing_php,
        "arity_mismatch": arity_mismatch,
        "docs_sync_missing": docs_sync_missing,
        "errors": errors,
    }
