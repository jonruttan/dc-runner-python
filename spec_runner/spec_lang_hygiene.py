from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from spec_runner.codecs import load_external_cases
from spec_runner.spec_domain import normalize_case_domain, normalize_export_symbol
from spec_runner.spec_lang_yaml_ast import SpecLangYamlAstError, compile_yaml_expr_to_sexpr

_GROUP_KEYS = {"MUST", "MAY", "MUST_NOT"}
_LEGACY_GROUP_KEYS = {"must", "can", "cannot"}
_WHEN_KEYS = {"must", "may", "must_not", "fail", "complete"}


@dataclass(frozen=True)
class SpecLangIssue:
    path: Path
    case_id: str
    field: str
    code: str
    message: str
    severity: str = "error"
    fixable: bool = False

    def render(self) -> str:
        return (
            f"{self.path.as_posix()}: case {self.case_id}: {self.code}: "
            f"{self.field}: {self.message}"
        )


class _FlowSeq(list):
    pass


class _FlowMap(dict):
    pass


class _CompactDumper(yaml.SafeDumper):
    pass


def _flow_seq_representer(dumper: yaml.Dumper, data: _FlowSeq) -> yaml.nodes.SequenceNode:
    return dumper.represent_sequence("tag:yaml.org,2002:seq", list(data), flow_style=True)


def _flow_map_representer(dumper: yaml.Dumper, data: _FlowMap) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping("tag:yaml.org,2002:map", dict(data), flow_style=True)


_CompactDumper.add_representer(_FlowSeq, _flow_seq_representer)
_CompactDumper.add_representer(_FlowMap, _flow_map_representer)


def iter_case_files(paths: list[Path], *, pattern: str) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_file():
            if p.match(pattern):
                out.append(p)
            continue
        if not p.exists():
            continue
        out.extend(sorted(x for x in p.rglob(pattern) if x.is_file()))
    seen: set[Path] = set()
    uniq: list[Path] = []
    for p in out:
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        uniq.append(p)
    return uniq


def _is_yaml_opening_fence(line: str) -> tuple[str, int] | None:
    stripped = line.lstrip(" \t")
    if not stripped:
        return None
    if stripped[0] not in ("`", "~"):
        return None
    ch = stripped[0]
    i = 0
    while i < len(stripped) and stripped[i] == ch:
        i += 1
    if i < 3:
        return None
    info = stripped[i:].strip().lower().split()
    if "yaml" not in info and "yml" not in info:
        return None
    if "contract-spec" not in info:
        return None
    return ch, i


def _is_closing_fence(line: str, *, ch: str, min_len: int) -> bool:
    stripped = line.lstrip(" \t").rstrip()
    if not stripped or stripped[0] != ch:
        return False
    i = 0
    while i < len(stripped) and stripped[i] == ch:
        i += 1
    return i >= min_len and i == len(stripped)


def _is_scalar(node: Any) -> bool:
    return isinstance(node, (str, int, float, bool)) or node is None


def _normalize_literal(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _normalize_literal(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_literal(v) for v in value]
    return value


def _is_operatorish_key(key: str) -> bool:
    s = str(key).strip()
    if not s:
        return False
    if s in {"var", "fn", "lit"}:
        return True
    return (
        "." in s
        or s.startswith("std.")
        or s.startswith("ops.")
        or s.startswith("core.")
        or s.startswith("json.")
    )


def _imports_map_to_list(bindings: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for local_name in sorted(bindings.keys()):
        spec = bindings.get(local_name)
        if not isinstance(spec, dict):
            continue
        src = str(spec.get("from", "")).strip()
        key = str(spec.get("key", "")).strip()
        if src not in {"artifact", "symbol"} or not key:
            continue
        bucket = grouped.setdefault(src, {"names": [], "as": {}})
        names = cast(list[str], bucket["names"])
        aliases = cast(dict[str, str], bucket["as"])
        if key not in names:
            names.append(key)
        if local_name != key:
            aliases[key] = local_name
    out: list[dict[str, Any]] = []
    for src in sorted(grouped.keys()):
        bucket = grouped[src]
        names = sorted(cast(list[str], bucket["names"]))
        aliases = {
            source: local
            for source, local in sorted(cast(dict[str, str], bucket["as"]).items())
            if source in names and source != local
        }
        item: dict[str, Any] = {"from": src, "names": names}
        if aliases:
            item["as"] = aliases
        out.append(item)
    return out


def _imports_any_to_map(raw_imports: Any) -> tuple[dict[str, dict[str, Any]], bool, bool]:
    """
    Returns (bindings, changed, valid_shape).
    bindings maps local_name -> {from, key} for supported import forms.
    """
    if raw_imports is None:
        return {}, False, True
    if isinstance(raw_imports, dict):
        out: dict[str, dict[str, Any]] = {}
        for raw_name, raw_spec in raw_imports.items():
            name = str(raw_name).strip()
            if not name or not isinstance(raw_spec, dict):
                return {}, False, False
            src = str(raw_spec.get("from", "")).strip()
            if src not in {"artifact", "symbol"}:
                return {}, False, False
            key = str(raw_spec.get("key", "")).strip()
            if not key:
                return {}, False, False
            out[name] = {"from": src, "key": key}
        return out, True, True
    if not isinstance(raw_imports, list):
        return {}, False, False
    out: dict[str, dict[str, Any]] = {}
    for raw_item in raw_imports:
        if not isinstance(raw_item, dict):
            return {}, False, False
        src = str(raw_item.get("from", "")).strip()
        if src not in {"artifact", "symbol"}:
            return {}, False, False
        raw_names = raw_item.get("names")
        if not isinstance(raw_names, list) or not raw_names:
            return {}, False, False
        raw_as = raw_item.get("as")
        alias_map: dict[str, str] = {}
        if raw_as is not None:
            if not isinstance(raw_as, dict):
                return {}, False, False
            for raw_k, raw_v in raw_as.items():
                source_name = str(raw_k).strip()
                local_name = str(raw_v).strip()
                if not source_name or not local_name:
                    return {}, False, False
                alias_map[source_name] = local_name
        for raw_name in raw_names:
            source_name = str(raw_name).strip()
            if not source_name:
                return {}, False, False
            local_name = alias_map.get(source_name, source_name)
            if not local_name:
                return {}, False, False
            out[local_name] = {"from": src, "key": source_name}
    return out, False, True


def _normalize_expr_node(node: Any) -> tuple[Any, bool]:
    changed = False
    if _is_scalar(node):
        return node, changed

    if isinstance(node, list):
        list_out: list[Any] = []
        for item in node:
            norm, ch = _normalize_expr_node(item)
            changed = changed or ch
            list_out.append(norm)
        return list_out, changed

    if not isinstance(node, dict):
        return node, changed

    if set(node.keys()) == {"evaluate"}:
        raw = node.get("evaluate")
        if isinstance(raw, dict):
            lifted, ch = _normalize_expr_node(raw)
            return lifted, True or ch
        if isinstance(raw, list) and len(raw) == 1 and isinstance(raw[0], dict):
            lifted, ch = _normalize_expr_node(raw[0])
            return lifted, True or ch

    if set(node.keys()) == {"lit"}:
        lit_value = node.get("lit")
        while isinstance(lit_value, dict) and set(lit_value.keys()) == {"lit"}:
            lit_value = lit_value.get("lit")
            changed = True
        lit_value = _normalize_literal(lit_value)
        if isinstance(lit_value, dict) and len(lit_value) == 1:
            raw_key = next(iter(lit_value.keys()))
            if _is_operatorish_key(str(raw_key)):
                lifted, ch = _normalize_expr_node(lit_value)
                return lifted, True or changed or ch
        if _is_scalar(lit_value):
            return _FlowMap({"lit": lit_value}), True or changed
        return {"lit": lit_value}, changed

    if len(node) == 1:
        op = str(next(iter(node.keys())))
        raw_args = node[op]
        if op == "var" and isinstance(raw_args, str):
            return _FlowMap({"var": raw_args.strip() or raw_args}), True
        if op == "fn" and isinstance(raw_args, list) and len(raw_args) == 2:
            params = raw_args[0]
            body = raw_args[1]
            if isinstance(params, dict) and set(params.keys()) == {"lit"} and isinstance(params.get("lit"), list):
                params = params.get("lit")
                changed = True
            norm_body, body_changed = _normalize_expr_node(body)
            changed = changed or body_changed
            if isinstance(params, list) and all(isinstance(x, str) and x.strip() for x in params):
                return {"fn": [_FlowSeq([str(x).strip() for x in params]), norm_body]}, True or changed
            norm_params, params_changed = _normalize_expr_node(params)
            changed = changed or params_changed
            return {"fn": [norm_params, norm_body]}, changed
        if isinstance(raw_args, list):
            args_out: list[Any] = []
            for arg in raw_args:
                norm_arg, ch = _normalize_expr_node(arg)
                changed = changed or ch
                args_out.append(norm_arg)
            return {op: args_out}, changed

    map_out: dict[str, Any] = {}
    for k, v in node.items():
        norm, ch = _normalize_expr_node(v)
        changed = changed or ch
        map_out[str(k)] = norm
    return map_out, changed


def _normalize_assert_node(node: Any) -> tuple[Any, bool]:
    changed = False
    if isinstance(node, list):
        list_out: list[Any] = []
        for child in node:
            norm, ch = _normalize_assert_node(child)
            changed = changed or ch
            list_out.append(norm)
        return list_out, changed
    if not isinstance(node, dict):
        return node, changed

    step_class = str(node.get("class", "")).strip() if "class" in node else ""
    if step_class in _GROUP_KEYS and "asserts" in node:
        step_out = dict(node)
        asserts = node.get("asserts")
        if isinstance(asserts, list):
            norm_asserts: list[Any] = []
            for child in asserts:
                norm, ch = _normalize_assert_node(child)
                changed = changed or ch
                if (
                    isinstance(norm, dict)
                    and set(norm.keys()) == {step_class}
                    and isinstance(norm.get(step_class), list)
                ):
                    changed = True
                    norm_asserts.extend(list(norm.get(step_class) or []))
                else:
                    norm_asserts.append(norm)
            step_out["asserts"] = norm_asserts
        return step_out, changed

    present = [k for k in _GROUP_KEYS if k in node]
    if present:
        group_out = dict(node)
        for key in present:
            raw_group_children = node.get(key)
            if not isinstance(raw_group_children, list):
                continue
            norm_children: list[Any] = []
            for child in raw_group_children:
                norm, ch = _normalize_assert_node(child)
                changed = changed or ch
                norm_children.append(norm)
            group_out[key] = norm_children
        return group_out, changed

    norm_expr, expr_changed = _normalize_expr_node(node)
    changed = changed or expr_changed
    if isinstance(norm_expr, dict) and set(norm_expr.keys()) == {"lit"}:
        inner = norm_expr.get("lit")
        if isinstance(inner, dict):
            mapped_key: str | None = None
            raw_lit_group_children: Any = None
            if "MUST" in inner:
                mapped_key = "MUST"
                raw_lit_group_children = inner.get("MUST")
            elif "MAY" in inner:
                mapped_key = "MAY"
                raw_lit_group_children = inner.get("MAY")
            elif "MUST_NOT" in inner:
                mapped_key = "MUST_NOT"
                raw_lit_group_children = inner.get("MUST_NOT")
            elif "must" in inner:
                mapped_key = "MUST"
                raw_lit_group_children = inner.get("must")
            elif "can" in inner:
                mapped_key = "MAY"
                raw_lit_group_children = inner.get("can")
            elif "cannot" in inner:
                mapped_key = "MUST_NOT"
                raw_lit_group_children = inner.get("cannot")
            if mapped_key and isinstance(raw_lit_group_children, list):
                normalized_children: list[Any] = []
                for child in raw_lit_group_children:
                    cnode, ch = _normalize_assert_node(child)
                    changed = changed or ch
                    normalized_children.append(cnode)
                return {mapped_key: normalized_children}, True
    return norm_expr, changed


def _collect_var_symbols(node: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(node, dict):
        if set(node.keys()) == {"var"}:
            name = str(node.get("var", "")).strip()
            if name:
                out.add(name)
        for value in node.values():
            out.update(_collect_var_symbols(value))
    elif isinstance(node, list):
        for item in node:
            out.update(_collect_var_symbols(item))
    return out


def _replace_var_symbol(node: Any, *, old: str, new: str) -> tuple[Any, bool]:
    changed = False
    if isinstance(node, dict):
        if set(node.keys()) == {"var"} and str(node.get("var", "")).strip() == old:
            return _FlowMap({"var": new}), True
        out: dict[str, Any] = {}
        for key, value in node.items():
            nval, ch = _replace_var_symbol(value, old=old, new=new)
            changed = changed or ch
            out[str(key)] = nval
        return out, changed
    if isinstance(node, list):
        out_list: list[Any] = []
        for item in node:
            nitem, ch = _replace_var_symbol(item, old=old, new=new)
            changed = changed or ch
            out_list.append(nitem)
        return out_list, changed
    return node, False


def _normalize_contract(node: Any) -> tuple[Any, bool]:
    changed = False
    if isinstance(node, dict):
        defaults_raw = node.get("defaults")
        defaults: dict[str, Any] = dict(defaults_raw) if isinstance(defaults_raw, dict) else {}
        contract_imports: dict[str, dict[str, Any]] = {}
        imports_raw = node.get("imports")
        contract_imports, imports_changed, imports_valid = _imports_any_to_map(imports_raw)
        changed = changed or imports_changed
        if not imports_valid:
            return node, changed
        nested_defaults: dict[str, Any] | None = None
        nested_steps: dict[str, Any] | None = None
        if isinstance(imports_raw, dict):
            raw_defaults = imports_raw.get("defaults")
            raw_steps = imports_raw.get("steps")
            nested_defaults = raw_defaults if isinstance(raw_defaults, dict) else None
            nested_steps = raw_steps if isinstance(raw_steps, dict) else None
            if raw_defaults is not None or raw_steps is not None:
                changed = True
        if isinstance(nested_defaults, dict):
            defaults_map, _, defaults_ok = _imports_any_to_map(nested_defaults)
            if defaults_ok:
                for key, value in defaults_map.items():
                    if key not in contract_imports:
                        contract_imports[key] = value
        default_target = ""
        if "target" in defaults:
            default_target = str(defaults.pop("target", "")).strip()
            changed = True
        elif "on" in defaults:
            default_target = str(defaults.pop("on", "")).strip()
            changed = True
        if default_target:
            if "subject" not in contract_imports:
                contract_imports["subject"] = {"from": "artifact", "key": default_target}
        defaults_imports = defaults.pop("imports", None)
        defaults_import_map, defaults_imports_changed, defaults_imports_valid = _imports_any_to_map(defaults_imports)
        changed = changed or defaults_imports_changed
        if defaults_imports is not None and not defaults_imports_valid:
            return node, changed
        if defaults_import_map:
            for key, value in defaults_import_map.items():
                if key not in contract_imports:
                    contract_imports[key] = value
            changed = True
        raw_steps = node.get("steps")
        if raw_steps is None:
            raw_steps = []
        if not isinstance(raw_steps, list):
            return node, changed
        steps_nested_imports: dict[str, Any] = {}
        if isinstance(nested_steps, dict):
            steps_nested_imports = nested_steps
        normalized_steps: list[dict[str, Any]] = []
        for idx, raw_step in enumerate(raw_steps):
            if not isinstance(raw_step, dict):
                normalized_steps.append({"id": f"step_{idx+1:03d}", "assert": raw_step})
                changed = True
                continue
            step = dict(raw_step)
            if "asserts" in step and "assert" not in step:
                step["assert"] = step.pop("asserts")
                changed = True
            step_target = ""
            if "target" in step:
                step_target = str(step.pop("target", "")).strip()
                changed = True
            elif "on" in step:
                step_target = str(step.pop("on", "")).strip()
                changed = True
            if step_target:
                imports_map, imports_map_changed, imports_map_valid = _imports_any_to_map(step.get("imports"))
                changed = changed or imports_map_changed
                if not imports_map_valid:
                    return node, changed
                if "subject" not in imports_map:
                    imports_map["subject"] = {"from": "artifact", "key": step_target}
                step["imports"] = imports_map
            raw_assert = step.get("assert")
            if isinstance(raw_assert, list):
                norm_asserts: list[Any] = []
                for child in raw_assert:
                    norm, ch = _normalize_assert_node(child)
                    changed = changed or ch
                    norm_asserts.append(norm)
                if len(norm_asserts) == 1:
                    step["assert"] = norm_asserts[0]
                    changed = True
                else:
                    step["assert"] = norm_asserts
            elif raw_assert is not None:
                norm, ch = _normalize_assert_node(raw_assert)
                changed = changed or ch
                step["assert"] = norm
            if "id" not in step or not str(step.get("id", "")).strip():
                step["id"] = f"step_{idx+1:03d}"
                changed = True
            step_id = str(step.get("id", "")).strip()
            if step_id and step_id in steps_nested_imports and isinstance(steps_nested_imports.get(step_id), dict):
                imports_map, imports_map_changed, imports_map_valid = _imports_any_to_map(step.get("imports"))
                changed = changed or imports_map_changed
                if not imports_map_valid:
                    return node, changed
                nested_map, _, nested_ok = _imports_any_to_map(cast(dict[str, Any], steps_nested_imports.get(step_id)))
                if not nested_ok:
                    return node, changed
                for key, value in nested_map.items():
                    if key not in imports_map:
                        imports_map[key] = value
                step["imports"] = imports_map
                changed = True
            step_class = str(step.get("class", "MUST")).strip() or "MUST"
            if step_class == "MUST" and "class" in step:
                step.pop("class", None)
                changed = True
            # Safe simplification: replace local alias subject -> artifact key in step scope.
            step_import_map, _, step_import_ok = _imports_any_to_map(step.get("imports"))
            if not step_import_ok:
                return node, changed
            subject_spec = step_import_map.get("subject")
            if isinstance(subject_spec, dict) and str(subject_spec.get("from", "")).strip() == "artifact":
                source_key = str(subject_spec.get("key", "")).strip()
                if source_key and source_key != "subject":
                    step_assert = step.get("assert")
                    refs = _collect_var_symbols(step_assert)
                    if "subject" in refs and source_key not in refs:
                        rewritten, ch = _replace_var_symbol(step_assert, old="subject", new=source_key)
                        changed = changed or ch
                        step["assert"] = rewritten
                        step_import_map.pop("subject", None)
                        if source_key not in step_import_map:
                            step_import_map[source_key] = {"from": "artifact", "key": source_key}
                        step["imports"] = step_import_map
                        changed = True
            normalized_steps.append(step)

        # Safe simplification: replace contract-level alias subject -> artifact key.
        subject_spec = contract_imports.get("subject")
        if isinstance(subject_spec, dict) and str(subject_spec.get("from", "")).strip() == "artifact":
            source_key = str(subject_spec.get("key", "")).strip()
            if source_key and source_key != "subject" and source_key not in contract_imports:
                can_rewrite_all = True
                for step in normalized_steps:
                    if not isinstance(step, dict):
                        continue
                    step_imports, _, step_ok = _imports_any_to_map(step.get("imports"))
                    if not step_ok:
                        can_rewrite_all = False
                        break
                    if "subject" in step_imports or source_key in step_imports:
                        can_rewrite_all = False
                        break
                    refs = _collect_var_symbols(step.get("assert"))
                    if "subject" in refs and source_key in refs:
                        can_rewrite_all = False
                        break
                if can_rewrite_all:
                    for step in normalized_steps:
                        if not isinstance(step, dict):
                            continue
                        refs = _collect_var_symbols(step.get("assert"))
                        if "subject" not in refs:
                            continue
                        rewritten, ch = _replace_var_symbol(step.get("assert"), old="subject", new=source_key)
                        changed = changed or ch
                        step["assert"] = rewritten
                    contract_imports.pop("subject", None)
                    contract_imports[source_key] = {"from": "artifact", "key": source_key}
                    changed = True

        # Canonical rule: step-level imports are overrides. If contract imports are
        # absent, seed them from the first observed step imports per symbol.
        if not contract_imports:
            for step in normalized_steps:
                raw_step_imports, _, raw_step_imports_valid = _imports_any_to_map(step.get("imports"))
                if not raw_step_imports_valid:
                    continue
                for name, spec in raw_step_imports.items():
                    if name not in contract_imports:
                        contract_imports[name] = spec
                        changed = True
        if contract_imports:
            for step in normalized_steps:
                raw_step_imports, _, raw_step_imports_valid = _imports_any_to_map(step.get("imports"))
                if not raw_step_imports_valid:
                    continue
                reduced = {
                    name: spec
                    for name, spec in raw_step_imports.items()
                    if name not in contract_imports or contract_imports.get(name) != spec
                }
                if reduced != raw_step_imports:
                    changed = True
                if reduced:
                    step["imports"] = reduced
                else:
                    step.pop("imports", None)

        if "class" not in defaults:
            defaults["class"] = "MUST"
        out: dict[str, Any] = {"defaults": defaults, "steps": normalized_steps}
        if contract_imports:
            out = {
                "defaults": defaults,
                "imports": _imports_map_to_list(contract_imports),
                "steps": normalized_steps,
            }
        for step in out.get("steps", []):
            if not isinstance(step, dict):
                continue
            imports_map, _, imports_ok = _imports_any_to_map(step.get("imports"))
            if not imports_ok:
                continue
            if imports_map:
                step["imports"] = _imports_map_to_list(imports_map)
            else:
                step.pop("imports", None)
        return out, True or changed

    if isinstance(node, list):
        # Legacy step-list migration shape.
        steps: list[dict[str, Any]] = []
        for idx, raw_step in enumerate(node):
            if not isinstance(raw_step, dict):
                steps.append({"id": f"step_{idx+1:03d}", "assert": raw_step})
                changed = True
                continue
            step = dict(raw_step)
            if "asserts" in step and "assert" not in step:
                step["assert"] = step.pop("asserts")
                changed = True
            step_target = ""
            if "target" in step:
                step_target = str(step.pop("target", "")).strip()
                changed = True
            elif "on" in step:
                step_target = str(step.pop("on", "")).strip()
                changed = True
            step_id = str(step.get("id", "")).strip() or f"step_{idx+1:03d}"
            step_class = str(step.get("class", "MUST")).strip() or "MUST"
            out_step: dict[str, Any] = {"id": step_id}
            if step_class != "MUST":
                out_step["class"] = step_class
            imports_map, imports_map_changed, imports_map_valid = _imports_any_to_map(step.get("imports"))
            changed = changed or imports_map_changed
            if not imports_map_valid:
                return node, changed
            if step_target and "subject" not in imports_map:
                imports_map["subject"] = {"from": "artifact", "key": step_target}
            if imports_map:
                out_step["imports"] = _imports_map_to_list(imports_map)
            raw_assert = step.get("assert")
            if isinstance(raw_assert, list):
                norm_asserts_v1: list[Any] = []
                for child in raw_assert:
                    norm, ch = _normalize_assert_node(child)
                    changed = changed or ch
                    norm_asserts_v1.append(norm)
                out_step["assert"] = (
                    norm_asserts_v1[0] if len(norm_asserts_v1) == 1 else norm_asserts_v1
                )
            else:
                norm, ch = _normalize_assert_node(raw_assert)
                changed = changed or ch
                out_step["assert"] = norm
            steps.append(out_step)
        return {"defaults": {"class": "MUST"}, "steps": steps}, True or changed
    return node, changed


def _normalize_case(case: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    out = dict(case)
    changed = False

    if "contract" in out:
        norm_contract, ch = _normalize_contract(out.get("contract"))
        out["contract"] = norm_contract
        changed = changed or ch

    when = out.get("when")
    if isinstance(when, dict):
        when_out: dict[str, Any] = {}
        for raw_key, raw_list in when.items():
            key = str(raw_key)
            if isinstance(raw_list, list):
                exprs: list[Any] = []
                for expr in raw_list:
                    norm, ch = _normalize_expr_node(expr)
                    changed = changed or ch
                    exprs.append(norm)
                when_out[key] = exprs
            else:
                when_out[key] = raw_list
        out["when"] = when_out

    defines = out.get("defines")
    if isinstance(defines, dict):
        def_out: dict[str, Any] = {}
        for scope, raw_map in defines.items():
            skey = str(scope)
            if isinstance(raw_map, dict):
                scope_out: dict[str, Any] = {}
                for raw_symbol, expr in raw_map.items():
                    sym = str(raw_symbol)
                    norm, ch = _normalize_expr_node(expr)
                    changed = changed or ch
                    scope_out[sym] = norm
                def_out[skey] = scope_out
            else:
                def_out[skey] = raw_map
        out["defines"] = def_out

    return out, changed


def normalize_case_payload(payload: Any) -> tuple[Any, bool]:
    if isinstance(payload, dict):
        return _normalize_case(payload)
    if isinstance(payload, list):
        changed = False
        out: list[Any] = []
        for item in payload:
            if isinstance(item, dict):
                norm, ch = _normalize_case(item)
                changed = changed or ch
                out.append(norm)
            else:
                out.append(item)
        return out, changed
    return payload, False


def _yaml_dump(payload: Any) -> str:
    return yaml.dump(payload, sort_keys=False, allow_unicode=False, width=88, Dumper=_CompactDumper)


def format_spec_markdown(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        opening = _is_yaml_opening_fence(lines[i])
        if not opening:
            out.append(lines[i])
            i += 1
            continue
        ch, fence_len = opening
        out.append(lines[i])
        i += 1
        block_lines: list[str] = []
        while i < len(lines) and not _is_closing_fence(lines[i], ch=ch, min_len=fence_len):
            block_lines.append(lines[i])
            i += 1

        if i >= len(lines):
            out.extend(block_lines)
            break

        block = "".join(block_lines)
        try:
            payload = yaml.safe_load(block)
            if payload is None:
                formatted = block.strip() + "\n"
            else:
                norm, _changed = normalize_case_payload(payload)
                formatted = _yaml_dump(norm)
        except yaml.YAMLError:
            formatted = block

        out.append(formatted)
        out.append(lines[i])
        i += 1

    return "".join(out)


def format_file(path: Path) -> tuple[str, bool]:
    original = path.read_text(encoding="utf-8")
    updated = format_spec_markdown(original)
    return updated, updated != original


def _append_issue(
    issues: list[SpecLangIssue],
    *,
    path: Path,
    case_id: str,
    field: str,
    code: str,
    message: str,
    fixable: bool = False,
) -> None:
    issues.append(
        SpecLangIssue(
            path=path,
            case_id=case_id,
            field=field,
            code=code,
            message=message,
            severity="error",
            fixable=fixable,
        )
    )


def _lint_direct_nested_lit(
    expr: Any,
    *,
    issues: list[SpecLangIssue],
    path: Path,
    case_id: str,
    field: str,
) -> None:
    if not isinstance(expr, dict):
        return

    depth = 0
    cur: Any = expr
    while isinstance(cur, dict) and set(cur.keys()) == {"lit"}:
        lit_value = cur.get("lit")
        depth += 1
        if depth >= 2:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=field,
                code="SLINT002",
                message="nested lit wrapper is forbidden",
                fixable=True,
            )
            break
        if isinstance(lit_value, dict) and len(lit_value) == 1:
            raw_key = next(iter(lit_value.keys()))
            if _is_operatorish_key(str(raw_key)):
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=field,
                    code="SLINT017",
                    message="operator-shaped lit wrapper is forbidden; use direct operator mapping",
                    fixable=True,
                )
        cur = lit_value


def _lint_expression_mapping(
    expr: Any,
    *,
    issues: list[SpecLangIssue],
    path: Path,
    case_id: str,
    field: str,
) -> None:
    if not isinstance(expr, dict) or not expr:
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field=field,
            code="SLINT004",
            message="expression leaf must be a non-empty operator mapping",
        )
        return
    if "evaluate" in expr:
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field=field,
            code="SLINT001",
            message="evaluate wrapper is forbidden; place operator mapping directly in assert",
            fixable=True,
        )
    for key in expr.keys():
        skey = str(key)
        if skey in _GROUP_KEYS or skey in _LEGACY_GROUP_KEYS:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{field}.{skey}",
                code="SLINT003",
                message="assertion group key is not a valid spec-lang operator in expression context",
            )

    _lint_direct_nested_lit(
        expr,
        issues=issues,
        path=path,
        case_id=case_id,
        field=field,
    )
    try:
        compile_yaml_expr_to_sexpr(expr, field_path=f"{path.as_posix()}::{case_id}.{field}")
    except SpecLangYamlAstError as exc:
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field=field,
            code="SLINT005",
            message=str(exc),
        )


def _lint_assert_node(
    node: Any,
    *,
    issues: list[SpecLangIssue],
    path: Path,
    case_id: str,
    field: str,
) -> None:
    if isinstance(node, list):
        for idx, child in enumerate(node):
            _lint_assert_node(
                child,
                issues=issues,
                path=path,
                case_id=case_id,
                field=f"{field}[{idx}]",
            )
        return
    if not isinstance(node, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field=field,
            code="SLINT006",
            message="assert node must be a mapping or list",
        )
        return

    step_class = str(node.get("class", "")).strip() if "class" in node else ""
    if step_class in _GROUP_KEYS and "asserts" in node:
        asserts = node.get("asserts")
        if not isinstance(asserts, list) or not asserts:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{field}.asserts",
                code="SLINT007",
                message="contract step asserts must be a non-empty list",
            )
            return
        for idx, child in enumerate(asserts):
            if isinstance(child, dict):
                nested_groups = [k for k in _GROUP_KEYS if k in child]
                if nested_groups:
                    only_same_class = (
                        set(child.keys()) == {step_class}
                        and isinstance(child.get(step_class), list)
                    )
                    if only_same_class:
                        _append_issue(
                            issues,
                            path=path,
                            case_id=case_id,
                            field=f"{field}.asserts[{idx}]",
                            code="SLINT018",
                            message="redundant nested group matches step class; flatten into asserts entries",
                            fixable=True,
                        )
                    else:
                        _append_issue(
                            issues,
                            path=path,
                            case_id=case_id,
                            field=f"{field}.asserts[{idx}]",
                            code="SLINT019",
                            message="nested assert groups are forbidden inside step asserts; use step class semantics",
                        )
            if (
                isinstance(child, dict)
                and set(child.keys()) == {step_class}
                and isinstance(child.get(step_class), list)
            ):
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{field}.asserts[{idx}]",
                    code="SLINT018",
                    message="redundant nested group matches step class; flatten into asserts entries",
                    fixable=True,
                )
            _lint_assert_node(
                child,
                issues=issues,
                path=path,
                case_id=case_id,
                field=f"{field}.asserts[{idx}]",
            )
        return

    present = [k for k in _GROUP_KEYS if k in node]
    legacy_present = [k for k in _LEGACY_GROUP_KEYS if k in node]
    if present or legacy_present:
        for bad in legacy_present:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{field}.{bad}",
                code="SLINT008",
                message="legacy lowercase group key is forbidden; use MUST/MAY/MUST_NOT",
            )
        if len(present) + len(legacy_present) > 1:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=field,
                code="SLINT009",
                message="assert group must include exactly one group key",
            )
        for key in present + legacy_present:
            children = node.get(key)
            if not isinstance(children, list) or not children:
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{field}.{key}",
                    code="SLINT010",
                    message="group value must be a non-empty list",
                )
                continue
            for idx, child in enumerate(children):
                _lint_assert_node(
                    child,
                    issues=issues,
                    path=path,
                    case_id=case_id,
                    field=f"{field}.{key}[{idx}]",
                )
        return

    _lint_expression_mapping(expr=node, issues=issues, path=path, case_id=case_id, field=field)


def _lint_when(case: dict[str, Any], *, issues: list[SpecLangIssue], path: Path, case_id: str) -> None:
    raw_when = case.get("when")
    if raw_when is None:
        return
    if not isinstance(raw_when, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="when",
            code="SLINT011",
            message="when must be a mapping",
        )
        return
    for raw_key, expr_list in raw_when.items():
        key = str(raw_key)
        if key not in _WHEN_KEYS:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"when.{key}",
                code="SLINT012",
                message="unknown when hook key",
            )
            continue
        if not isinstance(expr_list, list) or not expr_list:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"when.{key}",
                code="SLINT013",
                message="when hook value must be a non-empty list",
            )
            continue
        for idx, expr in enumerate(expr_list):
            _lint_expression_mapping(
                expr,
                issues=issues,
                path=path,
                case_id=case_id,
                field=f"when.{key}[{idx}]",
            )


def _lint_defines(case: dict[str, Any], *, issues: list[SpecLangIssue], path: Path, case_id: str) -> None:
    defines = case.get("defines")
    if defines is None:
        return
    if not isinstance(defines, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="defines",
            code="SLINT014",
            message="defines must be a mapping",
        )
        return
    for scope_name in ("public", "private"):
        scope = defines.get(scope_name)
        if scope is None:
            continue
        if not isinstance(scope, dict):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"defines.{scope_name}",
                code="SLINT015",
                message="defines scope must be a mapping",
            )
            continue
        for raw_symbol, expr in scope.items():
            symbol = str(raw_symbol).strip()
            if not symbol:
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"defines.{scope_name}",
                    code="SLINT016",
                    message="defines symbol name must be non-empty",
                )
                continue
            _lint_expression_mapping(
                expr,
                issues=issues,
                path=path,
                case_id=case_id,
                field=f"defines.{scope_name}.{symbol}",
            )


def _lint_library_export_docs(
    case: dict[str, Any],
    *,
    issues: list[SpecLangIssue],
    path: Path,
    case_id: str,
) -> None:
    if str(case.get("type", "")).strip() != "contract.export":
        return
    try:
        case_domain: str | None = normalize_case_domain(case.get("domain"))
    except (TypeError, ValueError):
        case_domain = None
    library = case.get("library")
    if not isinstance(library, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="library",
            code="SLINT033",
            message="contract.export requires library metadata mapping",
        )
        return
    stability = str(library.get("stability", "")).strip()
    if stability not in {"alpha", "beta", "stable", "internal"}:
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="library.stability",
            code="SLINT034",
            message="library.stability must be alpha|beta|stable|internal",
        )
    for req in ("id", "module", "owner"):
        if not str(library.get(req, "")).strip():
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"library.{req}",
                code="SLINT035",
                message=f"library.{req} must be non-empty",
            )

    harness = case.get("harness")
    exports = harness.get("exports") if isinstance(harness, dict) else None
    if not isinstance(exports, list) or not exports:
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="harness.exports",
            code="SLINT036",
            message="contract.export requires non-empty harness.exports list",
        )
        return
    canonical_symbols: dict[str, tuple[int, str]] = {}
    for idx, exp in enumerate(exports):
        efield = f"harness.exports[{idx}]"
        if not isinstance(exp, dict):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=efield,
                code="SLINT037",
                message="harness.exports entry must be mapping",
            )
            continue
        raw_as = str(exp.get("as", "")).strip()
        if raw_as:
            canonical = normalize_export_symbol(case_domain, raw_as)
            prior = canonical_symbols.get(canonical)
            if prior is not None:
                prior_idx, prior_raw = prior
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{efield}.as",
                    code="SLINT065",
                    message=(
                        "export symbol collides after domain prefixing "
                        f"(domain={case_domain or '<none>'}, raw_as={raw_as}, canonical={canonical}, "
                        f"prior=harness.exports[{prior_idx}].as={prior_raw})"
                    ),
                )
            else:
                canonical_symbols[canonical] = (idx, raw_as)
        params = exp.get("params")
        export_params: list[str] = []
        if not isinstance(params, list) or any(not isinstance(x, str) or not str(x).strip() for x in params):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.params",
                code="SLINT038",
                message="harness.exports[].params must be list of non-empty strings",
            )
        else:
            export_params = [str(x).strip() for x in params]
        doc = exp.get("doc")
        if not isinstance(doc, dict):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc",
                code="SLINT039",
                message="harness.exports[].doc must be mapping",
            )
            continue
        allowed = {
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
        unknown = sorted(str(k) for k in doc.keys() if str(k) not in allowed)
        if unknown:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc",
                code="SLINT040",
                message=f"unsupported doc keys: {', '.join(unknown)}",
            )
        if not str(doc.get("summary", "")).strip():
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc.summary",
                code="SLINT041",
                message="doc.summary must be non-empty",
            )
        if not str(doc.get("description", "")).strip():
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc.description",
                code="SLINT042",
                message="doc.description must be non-empty",
            )
        doc_params = doc.get("params")
        if not isinstance(doc_params, list) or not doc_params:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc.params",
                code="SLINT043",
                message="doc.params must be non-empty list",
            )
        else:
            names: list[str] = []
            for pidx, item in enumerate(doc_params):
                pfield = f"{efield}.doc.params[{pidx}]"
                if not isinstance(item, dict):
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=pfield,
                        code="SLINT044",
                        message="doc.params entry must be mapping",
                    )
                    continue
                name = str(item.get("name", "")).strip()
                if not name:
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"{pfield}.name",
                        code="SLINT045",
                        message="doc.params.name must be non-empty",
                    )
                if not str(item.get("type", "")).strip():
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"{pfield}.type",
                        code="SLINT046",
                        message="doc.params.type must be non-empty",
                    )
                if not str(item.get("description", "")).strip():
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"{pfield}.description",
                        code="SLINT047",
                        message="doc.params.description must be non-empty",
                    )
                if not isinstance(item.get("required"), bool):
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"{pfield}.required",
                        code="SLINT048",
                        message="doc.params.required must be bool",
                    )
                names.append(name)
            if names != export_params:
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{efield}.doc.params",
                    code="SLINT049",
                    message="doc.params names must exactly match harness.exports[].params",
                )
        returns = doc.get("returns")
        if not isinstance(returns, dict):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc.returns",
                code="SLINT050",
                message="doc.returns must be mapping",
            )
        errors = doc.get("errors")
        if not isinstance(errors, list) or not errors:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc.errors",
                code="SLINT051",
                message="doc.errors must be non-empty list",
            )
        examples = doc.get("examples")
        if not isinstance(examples, list) or not examples:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc.examples",
                code="SLINT052",
                message="doc.examples must be non-empty list",
            )
        portability = doc.get("portability")
        if not isinstance(portability, dict):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"{efield}.doc.portability",
                code="SLINT053",
                message="doc.portability must be mapping",
            )
        else:
            for runtime in ("python", "php", "rust"):
                if not isinstance(portability.get(runtime), bool):
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"{efield}.doc.portability.{runtime}",
                        code="SLINT054",
                        message=f"doc.portability.{runtime} must be bool",
                    )


def _lint_case_doc(
    case: dict[str, Any],
    *,
    issues: list[SpecLangIssue],
    path: Path,
    case_id: str,
) -> None:
    case_type = str(case.get("type", "")).strip()
    try:
        normalize_case_domain(case.get("domain"))
    except (TypeError, ValueError):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="domain",
            code="SLINT064",
            message="domain must be a non-empty string when provided",
        )
    raw_doc = case.get("doc")
    if case_type == "contract.export" and not isinstance(raw_doc, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="doc",
            code="SLINT055",
            message="contract.export requires root doc mapping",
        )
        return
    if raw_doc is None:
        return
    if not isinstance(raw_doc, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="doc",
            code="SLINT056",
            message="doc must be mapping",
        )
        return
    allowed = {"summary", "description", "audience", "since", "tags", "see_also", "deprecated"}
    unknown = sorted(str(k) for k in raw_doc.keys() if str(k) not in allowed)
    if unknown:
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="doc",
            code="SLINT057",
            message=f"unsupported doc keys: {', '.join(unknown)}",
        )
    if case_type != "contract.export":
        return
    for key in ("summary", "description", "audience", "since"):
        if not str(raw_doc.get(key, "")).strip():
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"doc.{key}",
                code="SLINT058",
                message=f"doc.{key} must be non-empty",
            )
    tags = raw_doc.get("tags")
    if tags is not None and (
        not isinstance(tags, list) or any(not isinstance(x, str) or not str(x).strip() for x in tags)
    ):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="doc.tags",
            code="SLINT059",
            message="doc.tags must be list of non-empty strings when provided",
        )
    see_also = raw_doc.get("see_also")
    if see_also is not None and (
        not isinstance(see_also, list)
        or any(not isinstance(x, str) or not str(x).strip() for x in see_also)
    ):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="doc.see_also",
            code="SLINT060",
            message="doc.see_also must be list of non-empty strings when provided",
        )
    deprecated = raw_doc.get("deprecated")
    if deprecated is None:
        return
    if not isinstance(deprecated, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="doc.deprecated",
            code="SLINT061",
            message="doc.deprecated must be mapping when provided",
        )
        return
    if not str(deprecated.get("replacement", "")).strip():
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="doc.deprecated.replacement",
            code="SLINT062",
            message="doc.deprecated.replacement must be non-empty",
        )
    if not str(deprecated.get("reason", "")).strip():
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="doc.deprecated.reason",
            code="SLINT063",
            message="doc.deprecated.reason must be non-empty",
        )


def _lint_contract(case: dict[str, Any], *, issues: list[SpecLangIssue], path: Path, case_id: str) -> None:
    case_type = str(case.get("type", "")).strip()
    def _collect_subject_refs(node: Any) -> int:
        if isinstance(node, dict):
            count = 0
            if set(node.keys()) == {"var"} and str(node.get("var", "")).strip() == "subject":
                count += 1
            for val in node.values():
                count += _collect_subject_refs(val)
            return count
        if isinstance(node, list):
            return sum(_collect_subject_refs(x) for x in node)
        return 0

    def _validate_imports(raw_imports: Any, *, field: str) -> set[str]:
        names: set[str] = set()
        if raw_imports is None:
            return names
        if not isinstance(raw_imports, list):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=field,
                code="SLINT080",
                message="imports must be a list when provided",
            )
            return names
        if not raw_imports:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=field,
                code="SLINT092",
                message=f"{field} must be omitted when empty",
                fixable=True,
            )
            return names
        for idx, raw_item in enumerate(raw_imports):
            if not isinstance(raw_item, dict):
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{field}[{idx}]",
                    code="SLINT082",
                    message="import item must be a mapping",
                )
                continue
            unknown = sorted(set(str(k) for k in raw_item.keys()) - {"from", "names", "as"})
            if unknown:
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{field}[{idx}]",
                    code="SLINT094",
                    message=f"import item has unknown keys: {', '.join(unknown)}",
                )
            src = str(raw_item.get("from", "")).strip()
            if src != "artifact":
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{field}[{idx}].from",
                    code="SLINT083",
                    message="assertion import from must be artifact",
                )
                continue
            raw_names = raw_item.get("names")
            if not isinstance(raw_names, list) or not raw_names:
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{field}[{idx}].names",
                    code="SLINT084",
                    message="import names is required and must be a non-empty list",
                )
                continue
            aliases = raw_item.get("as")
            alias_map: dict[str, str] = {}
            if aliases is not None:
                if not isinstance(aliases, dict):
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"{field}[{idx}].as",
                        code="SLINT095",
                        message="import as must be a mapping when provided",
                    )
                    continue
                for raw_key, raw_value in aliases.items():
                    source_name = str(raw_key).strip()
                    local_name = str(raw_value).strip()
                    if not source_name or not local_name:
                        _append_issue(
                            issues,
                            path=path,
                            case_id=case_id,
                            field=f"{field}[{idx}].as",
                            code="SLINT081",
                            message="import as keys and values must be non-empty strings",
                        )
                        continue
                    alias_map[source_name] = local_name
            source_names: set[str] = set()
            for name_idx, raw_name in enumerate(raw_names):
                source_name = str(raw_name).strip()
                if not source_name:
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"{field}[{idx}].names[{name_idx}]",
                        code="SLINT096",
                        message="import names entries must be non-empty strings",
                    )
                    continue
                source_names.add(source_name)
                local_name = alias_map.get(source_name, source_name)
                if local_name in names:
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"{field}[{idx}]",
                        code="SLINT097",
                        message=f"duplicate local import symbol: {local_name}",
                    )
                    continue
                names.add(local_name)
            unknown_aliases = sorted(k for k in alias_map.keys() if k not in source_names)
            if unknown_aliases:
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"{field}[{idx}].as",
                    code="SLINT098",
                    message=f"import as keys must be subset of names: {', '.join(unknown_aliases)}",
                )
        return names

    contract = case.get("contract")
    if contract is None:
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="contract",
            code="SLINT020",
            message="contract is required and must use mapping form",
        )
        return
    if isinstance(contract, list):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="contract",
            code="SLINT021",
            message="v1 list contract is forbidden; use contract.defaults + contract.steps",
            fixable=True,
        )
        return
    if not isinstance(contract, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="contract",
            code="SLINT022",
            message="contract must be a mapping with defaults and steps",
        )
        return
    contract_imports_raw = contract.get("imports")
    steps = contract.get("steps")
    if isinstance(steps, list):
        has_step_imports = any(isinstance(step, dict) and step.get("imports") is not None for step in steps)
        if has_step_imports and not isinstance(contract_imports_raw, list):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field="contract.imports",
                code="SLINT093",
                message="contract.imports is required when contract.steps[].imports is used",
                fixable=True,
            )
    defaults = contract.get("defaults")
    if defaults is not None and not isinstance(defaults, dict):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="contract.defaults",
            code="SLINT023",
            message="contract.defaults must be a mapping when provided",
        )
    contract_import_names = _validate_imports(contract.get("imports"), field="contract.imports")
    if isinstance(contract.get("imports"), dict):
        contract_imports = cast(dict[str, Any], contract.get("imports"))
        if "defaults" in contract_imports:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field="contract.imports.defaults",
                code="SLINT090",
                message="contract.imports.defaults is forbidden; use contract.imports directly",
                fixable=True,
            )
        if "steps" in contract_imports:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field="contract.imports.steps",
                code="SLINT091",
                message="contract.imports.steps is forbidden; use contract.steps[].imports",
                fixable=True,
            )
    if isinstance(defaults, dict):
        if "imports" in defaults:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field="contract.defaults.imports",
                code="SLINT089",
                message="contract.defaults.imports is forbidden; use contract.imports",
                fixable=True,
            )
        if "target" in defaults or "on" in defaults:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field="contract.defaults",
                code="SLINT086",
                message="contract.defaults target/on keys are forbidden; use contract.imports",
                fixable=True,
            )
    if not isinstance(steps, list):
        _append_issue(
            issues,
            path=path,
            case_id=case_id,
            field="contract.steps",
            code="SLINT024",
            message="contract.steps must be a list",
        )
        return
    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"contract.steps[{idx}]",
                code="SLINT025",
                message="contract step must be a mapping",
            )
            continue
        if "asserts" in step:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"contract.steps[{idx}].asserts",
                code="SLINT026",
                message="v1 step key asserts is forbidden; use assert",
                fixable=True,
            )
        if "on" in step:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"contract.steps[{idx}].on",
                code="SLINT027",
                message="contract step key on is forbidden; use imports",
                fixable=True,
            )
        if "target" in step:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"contract.steps[{idx}].target",
                code="SLINT087",
                message="contract step key target is forbidden; use imports",
                fixable=True,
            )
        step_import_names = _validate_imports(step.get("imports"), field=f"contract.steps[{idx}].imports")
        import_names = set(contract_import_names) | set(step_import_names)
        class_name = str(step.get("class", "MUST")).strip() or "MUST"
        if class_name not in _GROUP_KEYS:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"contract.steps[{idx}].class",
                code="SLINT028",
                message="contract step class must be MUST, MAY, or MUST_NOT",
            )
        raw_assert = step.get("assert")
        if raw_assert is None:
            _append_issue(
                issues,
                path=path,
                case_id=case_id,
                field=f"contract.steps[{idx}].assert",
                code="SLINT029",
                message="contract step assert is required",
            )
            continue
        if isinstance(raw_assert, list):
            if not raw_assert:
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"contract.steps[{idx}].assert",
                    code="SLINT030",
                    message="contract step assert list must be non-empty",
                )
                continue
            for aidx, expr in enumerate(raw_assert):
                _lint_assert_node(
                    expr,
                    issues=issues,
                    path=path,
                    case_id=case_id,
                    field=f"contract.steps[{idx}].assert[{aidx}]",
                )
                if (
                    case_type != "contract.export"
                    and _collect_subject_refs(expr) > 0
                    and "subject" not in import_names
                ):
                    _append_issue(
                        issues,
                        path=path,
                        case_id=case_id,
                        field=f"contract.steps[{idx}].assert[{aidx}]",
                        code="SLINT088",
                        message="var subject requires explicit imports.subject binding",
                        fixable=True,
                    )
        else:
            _lint_assert_node(
                raw_assert,
                issues=issues,
                path=path,
                case_id=case_id,
                field=f"contract.steps[{idx}].assert",
            )
            if (
                case_type != "contract.export"
                and _collect_subject_refs(raw_assert) > 0
                and "subject" not in import_names
            ):
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field=f"contract.steps[{idx}].assert",
                    code="SLINT088",
                    message="var subject requires explicit imports.subject binding",
                    fixable=True,
                )


def lint_cases(
    cases_path: Path,
    *,
    case_file_pattern: str,
    case_formats: set[str],
) -> list[SpecLangIssue]:
    issues: list[SpecLangIssue] = []
    for path, case in load_external_cases(
        cases_path,
        formats=case_formats,
        md_pattern=case_file_pattern,
    ):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        _lint_contract(case, issues=issues, path=path, case_id=case_id)
        _lint_library_export_docs(case, issues=issues, path=path, case_id=case_id)
        _lint_case_doc(case, issues=issues, path=path, case_id=case_id)
        harness = case.get("harness")
        if isinstance(harness, dict):
            if "chain" in harness:
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field="harness.chain",
                    code="SLINT031",
                    message="harness.chain is forbidden; use harness.use",
                    fixable=True,
                )
            raw_use = harness.get("use")
            if raw_use is not None and (not isinstance(raw_use, list) or not raw_use):
                _append_issue(
                    issues,
                    path=path,
                    case_id=case_id,
                    field="harness.use",
                    code="SLINT032",
                    message="harness.use must be a non-empty list when provided",
                )
        _lint_when(case, issues=issues, path=path, case_id=case_id)
        _lint_defines(case, issues=issues, path=path, case_id=case_id)

    return sorted(issues, key=lambda i: (i.path.as_posix(), i.case_id, i.field, i.code))
