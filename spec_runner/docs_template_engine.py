from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


_TOKEN_RE = re.compile(r"{{\s*([#\^\/]?)\s*([^{}]+?)\s*}}")


@dataclass(frozen=True)
class TemplateRenderError(ValueError):
    message: str

    def __str__(self) -> str:
        return self.message


def _lookup(stack: list[Any], path: str, *, strict: bool) -> Any:
    key = str(path).strip()
    if not key:
        raise TemplateRenderError("template variable must be non-empty")
    if key == ".":
        return stack[-1]
    parts = key.split(".")

    def _resolve(node: Any, part_list: list[str]) -> tuple[bool, Any]:
        cur = node
        for part in part_list:
            if isinstance(cur, dict):
                if part not in cur:
                    return False, None
                cur = cur[part]
            else:
                return False, None
        return True, cur

    for frame in reversed(stack):
        ok, value = _resolve(frame, parts)
        if ok:
            return value
    if strict:
        raise TemplateRenderError(f"missing template key: {key}")
    return ""


def _is_truthy(value: Any) -> bool:
    if value is None:
        return False
    if value is False:
        return False
    if value == "":
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


def _find_section_end(template: str, start: int, name: str) -> tuple[int, int]:
    depth = 1
    pos = start
    while True:
        m = _TOKEN_RE.search(template, pos)
        if m is None:
            raise TemplateRenderError(f"unclosed section: {name}")
        sigil = m.group(1)
        token_name = m.group(2).strip()
        if token_name == name:
            if sigil in {"#", "^"}:
                depth += 1
            elif sigil == "/":
                depth -= 1
                if depth == 0:
                    return m.start(), m.end()
        pos = m.end()


def _render_block(template: str, stack: list[Any], *, strict: bool) -> str:
    out: list[str] = []
    pos = 0
    while True:
        m = _TOKEN_RE.search(template, pos)
        if m is None:
            out.append(template[pos:])
            break
        out.append(template[pos:m.start()])
        sigil = m.group(1)
        name = m.group(2).strip()
        if sigil == "":
            value = _lookup(stack, name, strict=strict)
            if isinstance(value, (dict, list)):
                out.append(str(value))
            elif isinstance(value, bool):
                out.append("true" if value else "false")
            elif value is None:
                out.append("")
            else:
                out.append(str(value))
            pos = m.end()
            continue
        if sigil in {"#", "^"}:
            section_start = m.end()
            body_end, close_end = _find_section_end(template, section_start, name)
            body = template[section_start:body_end]
            value = _lookup(stack, name, strict=strict)
            truthy = _is_truthy(value)
            if sigil == "#":
                if isinstance(value, list):
                    for item in value:
                        out.append(_render_block(body, [*stack, item], strict=strict))
                elif truthy:
                    if isinstance(value, dict):
                        out.append(_render_block(body, [*stack, value], strict=strict))
                    else:
                        out.append(_render_block(body, stack, strict=strict))
            else:  # inverted
                if not truthy:
                    out.append(_render_block(body, stack, strict=strict))
            pos = close_end
            continue
        if sigil == "/":
            raise TemplateRenderError(f"unexpected section close: {name}")
    return "".join(out)


def render_moustache(template: str, context: dict[str, Any], *, strict: bool = True) -> str:
    if not isinstance(context, dict):
        raise TemplateRenderError("template context must be a mapping")
    return _render_block(str(template), [context], strict=strict)
