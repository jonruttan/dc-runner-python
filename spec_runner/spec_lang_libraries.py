from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spec_runner.codecs import load_external_cases
from spec_runner.external_refs import resolve_external_ref
from spec_runner.spec_lang import SpecLangLimits, compile_symbol_bindings
from spec_runner.spec_lang_yaml_ast import SpecLangYamlAstError, compile_yaml_expr_to_sexpr
from spec_runner.virtual_paths import VirtualPathError, contract_root_for, parse_external_ref, resolve_contract_path


@dataclass(frozen=True)
class _LibraryDoc:
    path: Path
    imports: tuple[str, ...]
    bindings: dict[str, Any]
    exports: tuple[str, ...]


def _resolve_library_path(
    base_doc: Path,
    rel_path: str,
    *,
    harness: dict[str, Any] | None,
    requires: dict[str, Any] | None,
) -> Path:
    raw = str(rel_path).strip()
    if parse_external_ref(raw) is not None:
        try:
            p = resolve_external_ref(raw, harness=harness, requires=requires)
        except VirtualPathError as exc:
            raise ValueError(str(exc)) from exc
    else:
        root = contract_root_for(base_doc)
        try:
            p = resolve_contract_path(root, raw, field="harness.spec_lang.includes")
        except VirtualPathError as exc:
            raise ValueError(str(exc)) from exc
    if not p.exists() or not p.is_file():
        raise ValueError(f"library path does not exist: {rel_path}")
    return p


def _as_non_empty_str_list(value: object, *, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise TypeError(f"{field} must be a list of non-empty strings")
    out: list[str] = []
    for i, item in enumerate(value):
        s = str(item).strip() if isinstance(item, str) else ""
        if not s:
            raise TypeError(f"{field}[{i}] must be a non-empty string")
        out.append(s)
    return tuple(out)


def _load_library_doc(path: Path) -> _LibraryDoc:
    loaded = load_external_cases(path, formats={"md", "yaml", "json"})
    imports: list[str] = []
    bindings: dict[str, Any] = {}
    exports: list[str] = []

    def _compile_definition_scope(raw_scope: object, *, field_path: str) -> dict[str, Any]:
        if raw_scope is None:
            return {}
        if not isinstance(raw_scope, dict):
            raise TypeError(f"spec_lang.export {field_path} must be a mapping when provided")
        out: dict[str, Any] = {}
        for raw_name, expr in raw_scope.items():
            name = str(raw_name).strip()
            if not name:
                raise ValueError(f"spec_lang.export {field_path} symbol name must be non-empty")
            if name in out:
                raise ValueError(
                    "spec_lang.export duplicate symbol inside scope "
                    f"{field_path}: {name}"
                )
            try:
                out[name] = compile_yaml_expr_to_sexpr(
                    expr,
                    field_path=f"{path.as_posix()} {field_path}.{name}",
                )
            except SpecLangYamlAstError as exc:
                raise ValueError(str(exc)) from exc
        return out

    for _, case in loaded:
        case_type = str(case.get("type", "")).strip()
        if case_type != "spec_lang.export":
            continue

        case_imports = _as_non_empty_str_list(case.get("imports"), field="imports")
        imports.extend(case_imports)

        if "definitions" in case:
            raise TypeError(
                "spec_lang.export legacy key 'definitions' is not supported; use 'defines'"
            )
        raw_defines = case.get("defines")
        if not isinstance(raw_defines, dict):
            raise TypeError("spec_lang.export requires defines mapping with public/private scopes")
        public_bindings = _compile_definition_scope(
            raw_defines.get("public"), field_path="defines.public"
        )
        private_bindings = _compile_definition_scope(
            raw_defines.get("private"), field_path="defines.private"
        )
        if not public_bindings and not private_bindings:
            raise TypeError(
                "spec_lang.export requires non-empty defines.public or defines.private mapping"
            )
        overlap = sorted(set(public_bindings).intersection(private_bindings))
        if overlap:
            raise ValueError(
                "spec_lang.export duplicate symbol across defines.public/defines.private: "
                + ", ".join(overlap)
            )
        for name, expr in {**public_bindings, **private_bindings}.items():
            if name in bindings:
                if bindings[name] == expr:
                    continue
                raise ValueError(f"duplicate library symbol in file {path}: {name}")
            bindings[name] = expr
        exports.extend(sorted(public_bindings.keys()))

    if not bindings:
        raise ValueError(f"library file has no spec_lang.export defines: {path}")

    return _LibraryDoc(
        path=path,
        imports=tuple(dict.fromkeys(imports)),
        bindings=bindings,
        exports=tuple(dict.fromkeys(exports)),
    )


def compile_library_case_public_symbols(
    *,
    raw_case: dict[str, Any],
    source_path: Path,
    limits: SpecLangLimits,
) -> dict[str, Any]:
    case_type = str(raw_case.get("type", "")).strip()
    if case_type != "spec_lang.export":
        raise TypeError("library symbol export requires type spec_lang.export case")
    if "definitions" in raw_case:
        raise TypeError(
            "spec_lang.export legacy key 'definitions' is not supported; use 'defines'"
        )
    raw_defines = raw_case.get("defines")
    if not isinstance(raw_defines, dict):
        raise TypeError("spec_lang.export requires defines mapping with public/private scopes")
    raw_public = raw_defines.get("public")
    raw_private = raw_defines.get("private")
    if raw_public is None and raw_private is None:
        raise TypeError("spec_lang.export requires defines.public or defines.private mapping")
    if raw_public is not None and not isinstance(raw_public, dict):
        raise TypeError("spec_lang.export defines.public must be mapping when provided")
    if raw_private is not None and not isinstance(raw_private, dict):
        raise TypeError("spec_lang.export defines.private must be mapping when provided")
    public_map = dict(raw_public or {})
    private_map = dict(raw_private or {})
    overlap = sorted(set(public_map).intersection(private_map))
    if overlap:
        raise ValueError(
            "spec_lang.export duplicate symbol across defines.public/defines.private: "
            + ", ".join(overlap)
        )
    if not public_map and not private_map:
        raise TypeError("spec_lang.export requires non-empty defines.public or defines.private mapping")
    merged_raw: dict[str, Any] = {}
    for scope_name, scope in (("defines.public", public_map), ("defines.private", private_map)):
        for raw_name, expr in scope.items():
            name = str(raw_name).strip()
            if not name:
                raise ValueError(f"spec_lang.export {scope_name} symbol name must be non-empty")
            if name in merged_raw:
                raise ValueError(f"duplicate library symbol in case {source_path}: {name}")
            try:
                merged_raw[name] = compile_yaml_expr_to_sexpr(
                    expr,
                    field_path=f"{source_path.as_posix()} {scope_name}.{name}",
                )
            except SpecLangYamlAstError as exc:
                raise ValueError(str(exc)) from exc
    compiled = compile_symbol_bindings(merged_raw, limits=limits)
    return {k: compiled[k] for k in public_map.keys()}


def _resolve_library_graph(
    entry_docs: list[Path], *, harness: dict[str, Any] | None, requires: dict[str, Any] | None
) -> list[_LibraryDoc]:
    docs: dict[Path, _LibraryDoc] = {}
    visiting: set[Path] = set()
    visited: set[Path] = set()
    ordered: list[Path] = []

    def _dfs(path: Path) -> None:
        if path in visited:
            return
        if path in visiting:
            raise ValueError(f"library import cycle detected at: {path}")
        visiting.add(path)
        doc = docs.get(path)
        if doc is None:
            doc = _load_library_doc(path)
            docs[path] = doc
        for rel in doc.imports:
            dep = _resolve_library_path(path, rel, harness=harness, requires=requires)
            _dfs(dep)
        visiting.remove(path)
        visited.add(path)
        ordered.append(path)

    for p in entry_docs:
        _dfs(p)

    return [docs[p] for p in ordered]


def load_spec_lang_symbols_for_case(
    *,
    doc_path: Path,
    harness: dict[str, Any] | None,
    limits: SpecLangLimits,
) -> dict[str, Any]:
    cfg = dict((harness or {}).get("spec_lang") or {})
    lib_paths = _as_non_empty_str_list(cfg.get("includes"), field="harness.spec_lang.includes")
    if not lib_paths:
        return {}
    requires = dict((harness or {}).get("requires") or {})

    entry_docs = [
        _resolve_library_path(doc_path, rel, harness=harness, requires=requires) for rel in lib_paths
    ]
    graph = _resolve_library_graph(entry_docs, harness=harness, requires=requires)

    merged_bindings: dict[str, Any] = {}
    export_allow: set[str] = set()
    for doc in graph:
        for name, expr in doc.bindings.items():
            if name in merged_bindings:
                raise ValueError(f"duplicate exported library symbol across imports: {name}")
            merged_bindings[name] = expr
        if doc.exports:
            export_allow.update(doc.exports)

    consumer_exports = _as_non_empty_str_list(cfg.get("exports"), field="harness.spec_lang.exports")
    if consumer_exports:
        export_allow = set(consumer_exports)

    unknown = sorted(x for x in export_allow if x not in merged_bindings)
    if unknown:
        raise ValueError("harness.spec_lang.exports contains unknown symbols: " + ", ".join(unknown))

    compiled = compile_symbol_bindings(merged_bindings, limits=limits)
    if export_allow:
        return {k: v for k, v in compiled.items() if k in export_allow}
    return compiled
