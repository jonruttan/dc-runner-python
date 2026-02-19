from __future__ import annotations

from typing import Any


class SpecLangYamlAstError(ValueError):
    pass


def _compile_node(node: Any, *, field_path: str) -> Any:
    if isinstance(node, (str, int, float, bool)) or node is None:
        return node

    if isinstance(node, list):
        raise SpecLangYamlAstError(
            f"{field_path}: list expressions are not allowed; use operator-keyed mapping AST and wrap literal lists with lit"
        )

    if not isinstance(node, dict):
        raise SpecLangYamlAstError(
            f"{field_path}: expression node must be scalar or mapping"
        )

    keys = list(node.keys())
    if not keys:
        raise SpecLangYamlAstError(f"{field_path}: expression mapping must not be empty")

    if "lit" in node:
        if len(keys) != 1:
            raise SpecLangYamlAstError(
                f"{field_path}: lit wrapper must be the only key in a mapping"
            )
        lit_value = node["lit"]
        if isinstance(lit_value, dict):
            out: dict[str, Any] = {}
            for k, v in lit_value.items():
                out[str(k)] = _compile_literal_value(v, field_path=f"{field_path}.lit.{k}")
            return ["lit", out]
        if isinstance(lit_value, list):
            return ["lit", [
                _compile_literal_value(v, field_path=f"{field_path}.lit[{idx}]")
                for idx, v in enumerate(lit_value)
            ]]
        return ["lit", lit_value]

    if len(keys) != 1:
        raise SpecLangYamlAstError(
            f"{field_path}: expression mapping must have exactly one operator key"
        )

    op = str(keys[0]).strip()
    if not op:
        raise SpecLangYamlAstError(f"{field_path}: operator key must be non-empty")
    if op == "var":
        symbol = node[keys[0]]
        if not isinstance(symbol, str) or not symbol.strip():
            raise SpecLangYamlAstError(
                f"{field_path}.var: variable name must be a non-empty string"
            )
        return ["var", symbol.strip()]
    raw_args = node[keys[0]]
    if op == "fn":
        if not isinstance(raw_args, list) or len(raw_args) != 2:
            raise SpecLangYamlAstError(
                f"{field_path}.fn: fn args must be [params, body]"
            )
        raw_params = raw_args[0]
        if not isinstance(raw_params, list):
            raise SpecLangYamlAstError(
                f"{field_path}.fn[0]: params must be a list of variable names"
            )
        params: list[str] = []
        for idx, value in enumerate(raw_params):
            if not isinstance(value, str) or not value.strip():
                raise SpecLangYamlAstError(
                    f"{field_path}.fn[0][{idx}]: param name must be a non-empty string"
                )
            params.append(value.strip())
        body = _compile_node(raw_args[1], field_path=f"{field_path}.fn[1]")
        return ["fn", params, body]
    if not isinstance(raw_args, list):
        raise SpecLangYamlAstError(
            f"{field_path}.{op}: operator args must be a list"
        )

    compiled_args = [
        _compile_node(arg, field_path=f"{field_path}.{op}[{idx}]")
        for idx, arg in enumerate(raw_args)
    ]
    return [op, *compiled_args]


def _compile_literal_value(value: Any, *, field_path: str) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            out[str(k)] = _compile_literal_value(v, field_path=f"{field_path}.{k}")
        return out
    if isinstance(value, list):
        return [_compile_literal_value(v, field_path=f"{field_path}[{idx}]") for idx, v in enumerate(value)]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise SpecLangYamlAstError(f"{field_path}: unsupported literal value type")


def compile_yaml_expr_to_sexpr(node: Any, *, field_path: str) -> Any:
    """Compile one mapping-AST expression node into internal list-token s-expr."""
    return _compile_node(node, field_path=field_path)


def compile_yaml_expr_list(nodes: list[Any], *, field_path: str) -> list[Any]:
    """Compile a list of mapping-AST expression nodes into internal s-expr nodes."""
    if not isinstance(nodes, list) or not nodes:
        raise SpecLangYamlAstError(f"{field_path}: expression list must be a non-empty list")
    out: list[Any] = []
    for idx, node in enumerate(nodes):
        out.append(_compile_node(node, field_path=f"{field_path}[{idx}]"))
    return out


def is_sexpr_node(node: Any) -> bool:
    return isinstance(node, list) and len(node) > 0 and isinstance(node[0], str) and bool(node[0])


def sexpr_to_yaml_ast(node: Any) -> Any:
    if isinstance(node, (str, int, float, bool)) or node is None:
        return node
    if isinstance(node, list):
        if is_sexpr_node(node):
            op = str(node[0])
            if op == "subject" and len(node) == 1:
                return {"var": "subject"}
            if op == "var" and len(node) == 2 and isinstance(node[1], str) and node[1].strip():
                return {"var": node[1].strip()}
            if op == "lit" and len(node) == 2:
                return {"lit": _literalize(node[1])}
            if op == "fn" and len(node) == 3 and isinstance(node[1], list):
                params: list[str] = []
                for idx, value in enumerate(node[1]):
                    if not isinstance(value, str) or not value.strip():
                        raise SpecLangYamlAstError(
                            f"sexpr.fn[1][{idx}]: param name must be a non-empty string"
                        )
                    params.append(value.strip())
                body = sexpr_to_yaml_ast(node[2])
                return {"fn": [params, body]}
            args = [sexpr_to_yaml_ast(arg) for arg in node[1:]]
            return {op: args}
        return {"lit": [_literalize(v) for v in node]}
    if isinstance(node, dict):
        return {"lit": {str(k): _literalize(v) for k, v in node.items()}}
    return node


def _literalize(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_literalize(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _literalize(v) for k, v in value.items()}
    return value
