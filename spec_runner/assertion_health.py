from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from spec_runner.settings import SETTINGS

@dataclass(frozen=True)
class AssertionHealthDiagnostic:
    code: str
    message: str
    path: str


_ALWAYS_TRUE_REGEX = {".*", "^.*$", r"\A.*\Z"}
_VALID_MODES = {"ignore", "warn", "error"}
_NON_PORTABLE_REGEX_TOKENS: tuple[tuple[str, str], ...] = (
    (r"\(\?<=|\(\?<!", "lookbehind"),
    (r"\(\?P<|\(\?<([A-Za-z_][A-Za-z0-9_]*)>", "named capture group"),
    (r"\\k<", "named backreference"),
    (r"\(\?\(", "conditional group"),
    (r"\(\?[aiLmsux-]+:|\(\?[aiLmsux-]+\)", "inline flags"),
    (r"\(\?>", "atomic group"),
    (r"(?<!\\)(?:\\\\)*[+*?]\+", "possessive quantifier"),
)


def resolve_assert_health_mode(test: dict[str, Any], *, env: dict[str, str]) -> str:
    default_mode = SETTINGS.assertion_health.default_mode
    mode = str(env.get(SETTINGS.env.assert_health, default_mode)).strip().lower() or default_mode
    cfg = test.get("assert_health")
    if cfg is not None:
        if not isinstance(cfg, dict):
            raise TypeError("assert_health must be a mapping when provided")
        if "mode" in cfg:
            mode = str(cfg.get("mode", "")).strip().lower()
    if mode not in _VALID_MODES:
        raise ValueError("assert_health.mode must be one of: ignore, warn, error")
    return mode


def lint_assert_tree(assert_spec: Any) -> list[AssertionHealthDiagnostic]:
    out: list[AssertionHealthDiagnostic] = []

    def _walk(node: Any, *, path: str, group_ctx: str | None) -> None:
        if node is None:
            return
        if isinstance(node, list):
            for i, child in enumerate(node):
                _walk(child, path=f"{path}[{i}]", group_ctx=group_ctx)
            return
        if not isinstance(node, dict):
            return

        if "steps" in node and isinstance(node.get("steps"), list):
            _walk(node.get("steps"), path=f"{path}.steps", group_ctx=group_ctx)
            return

        step_class = str(node.get("class", "")).strip() if "class" in node else ""
        if step_class in {"MUST", "MAY", "MUST_NOT"} and "asserts" in node:
            asserts = node.get("asserts")
            if isinstance(asserts, list):
                step_seen: set[str] = set()
                for child in asserts:
                    try:
                        import json

                        key = json.dumps(child, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
                    except (TypeError, ValueError):
                        key = repr(child)
                    if key in step_seen:
                        out.append(
                            AssertionHealthDiagnostic(
                                code="AH004",
                                message=f"redundant sibling assertion branch in '{step_class}'",
                                path=f"{path}.asserts",
                            )
                        )
                        break
                    step_seen.add(key)
            _walk(asserts, path=f"{path}.asserts", group_ctx=step_class)
            return
        if step_class in {"MUST", "MAY", "MUST_NOT"} and "assert" in node:
            asserts = node.get("assert")
            checks = asserts if isinstance(asserts, list) else [asserts]
            step_seen_assert: set[str] = set()
            for child in checks:
                try:
                    import json

                    key = json.dumps(child, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
                except (TypeError, ValueError):
                    key = repr(child)
                if key in step_seen_assert:
                    out.append(
                        AssertionHealthDiagnostic(
                            code="AH004",
                            message=f"redundant sibling assertion branch in '{step_class}'",
                            path=f"{path}.assert",
                        )
                    )
                    break
                step_seen_assert.add(key)
            _walk(asserts, path=f"{path}.assert", group_ctx=step_class)
            return

        group_key = None
        for k in ("MUST", "MAY", "MUST_NOT"):
            if k in node:
                group_key = k
                break
        if group_key:
            children = node.get(group_key)
            if isinstance(children, list):
                group_seen: set[str] = set()
                for child in children:
                    try:
                        import json

                        key = json.dumps(child, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
                    except (TypeError, ValueError):
                        key = repr(child)
                    if key in group_seen:
                        out.append(
                            AssertionHealthDiagnostic(
                                code="AH004",
                                message=f"redundant sibling assertion branch in '{group_key}'",
                                path=f"{path}.{group_key}",
                            )
                        )
                        break
                    group_seen.add(key)
            _walk(children, path=f"{path}.{group_key}", group_ctx=group_key)
            return

        for op in ("contain", "regex"):
            if op not in node:
                continue
            raw = node.get(op)
            if not isinstance(raw, list):
                continue
            vals = [str(v) for v in raw]
            if len(vals) != len(set(vals)):
                out.append(
                    AssertionHealthDiagnostic(
                        code="AH003",
                        message=f"duplicate values in '{op}' list can hide intent drift",
                        path=f"{path}.{op}",
                    )
                )
            if op == "contain" and "" in vals:
                code = "AH001"
                msg = "contain with empty string is always true"
                if group_ctx == "MUST_NOT":
                    msg = "MUST_NOT(contain:'') is always false"
                out.append(AssertionHealthDiagnostic(code=code, message=msg, path=f"{path}.contain"))
            if op == "regex":
                for v in vals:
                    if v in _ALWAYS_TRUE_REGEX:
                        code = "AH002"
                        msg = "regex pattern is trivially always true"
                        if group_ctx == "MUST_NOT":
                            msg = "MUST_NOT(regex always-true) is always false"
                        out.append(AssertionHealthDiagnostic(code=code, message=msg, path=f"{path}.regex"))
                    for pattern, reason in _NON_PORTABLE_REGEX_TOKENS:
                        if re.search(pattern, v):
                            out.append(
                                AssertionHealthDiagnostic(
                                    code="AH005",
                                    message=f"regex uses non-portable construct ({reason})",
                                    path=f"{path}.regex",
                                )
                            )
                            break

    _walk(assert_spec, path="contract", group_ctx=None)
    return out


def format_assertion_health_warning(d: AssertionHealthDiagnostic) -> str:
    return f"WARN: ASSERT_HEALTH {d.code} at {d.path}: {d.message}"


def format_assertion_health_error(diags: list[AssertionHealthDiagnostic]) -> str:
    details = "; ".join(f"{d.code}@{d.path}" for d in diags)
    return f"assertion health check failed ({len(diags)} issue(s)): {details}"
