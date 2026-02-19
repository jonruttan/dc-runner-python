from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shlex
from typing import Any

import yaml
from spec_runner.virtual_paths import VirtualPathError, resolve_contract_path


@dataclass(frozen=True)
class DocsIssue:
    path: str
    line: int
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


_DOC_ID_RE = re.compile(r"^DOC-[A-Z0-9]+-\d{3}$")
_EXAMPLE_ID_RE = re.compile(r"^EX-[A-Z0-9-]+$")
_MARKER_RE = re.compile(r"DOCS-EXAMPLE-OPT-OUT:\s*(.+)")


def _is_fence_opening(line: str) -> tuple[str, int, list[str]] | None:
    stripped = line.lstrip(" \t")
    if not stripped or stripped[0] not in {"`", "~"}:
        return None
    ch = stripped[0]
    i = 0
    while i < len(stripped) and stripped[i] == ch:
        i += 1
    if i < 3:
        return None
    info = stripped[i:].strip().lower().split()
    return ch, i, info


def _is_fence_closing(line: str, *, ch: str, min_len: int) -> bool:
    stripped = line.lstrip(" \t").rstrip()
    if not stripped or stripped[0] != ch:
        return False
    i = 0
    while i < len(stripped) and stripped[i] == ch:
        i += 1
    return i >= min_len and i == len(stripped)


def _iter_fenced_blocks(text: str) -> list[tuple[int, int, list[str], list[str]]]:
    lines = text.splitlines()
    blocks: list[tuple[int, int, list[str], list[str]]] = []
    i = 0
    while i < len(lines):
        opening = _is_fence_opening(lines[i])
        if not opening:
            i += 1
            continue
        ch, fence_len, info = opening
        start = i
        i += 1
        block_lines: list[str] = []
        while i < len(lines) and not _is_fence_closing(lines[i], ch=ch, min_len=fence_len):
            block_lines.append(lines[i])
            i += 1
        end = i
        blocks.append((start + 1, end + 1, info, block_lines))
        i += 1
    return blocks


def _parse_front_matter(text: str) -> tuple[dict[str, Any] | None, int]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return None, 1
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, 1
    payload = "\n".join(lines[1:end])
    parsed = yaml.safe_load(payload)
    if isinstance(parsed, dict):
        return parsed, 2
    return None, 1


def extract_doc_meta(text: str) -> tuple[dict[str, Any] | None, int]:
    fm_meta, fm_line = _parse_front_matter(text)
    if fm_meta is not None:
        return fm_meta, fm_line
    for start, _end, info, block_lines in _iter_fenced_blocks(text):
        if "doc-meta" in info and ("yaml" in info or "yml" in info):
            parsed = yaml.safe_load("\n".join(block_lines))
            if isinstance(parsed, dict):
                return parsed, start
            return None, start
    return None, 1


def validate_doc_meta(rel: str, meta: dict[str, Any], *, line: int) -> list[DocsIssue]:
    issues: list[DocsIssue] = []
    doc_id = str(meta.get("doc_id", "")).strip()
    title = str(meta.get("title", "")).strip()
    status = str(meta.get("status", "")).strip()
    audience = str(meta.get("audience", "")).strip()
    owns_tokens = meta.get("owns_tokens")
    requires_tokens = meta.get("requires_tokens")
    commands = meta.get("commands")
    examples = meta.get("examples")
    sections_required = meta.get("sections_required")

    if not _DOC_ID_RE.fullmatch(doc_id):
        issues.append(DocsIssue(rel, line, "doc-meta.doc_id must match DOC-<AREA>-###"))
    if not title:
        issues.append(DocsIssue(rel, line, "doc-meta.title must be non-empty"))
    if status not in {"active", "draft"}:
        issues.append(DocsIssue(rel, line, "doc-meta.status must be active|draft"))
    if audience not in {"author", "reviewer", "maintainer"}:
        issues.append(DocsIssue(rel, line, "doc-meta.audience must be author|reviewer|maintainer"))

    for field_name, value in (("owns_tokens", owns_tokens), ("requires_tokens", requires_tokens)):
        if not isinstance(value, list):
            issues.append(DocsIssue(rel, line, f"doc-meta.{field_name} must be a list"))
            continue
        for item in value:
            if not isinstance(item, str) or not item.strip():
                issues.append(DocsIssue(rel, line, f"doc-meta.{field_name} entries must be non-empty strings"))
                break

    if not isinstance(commands, list):
        issues.append(DocsIssue(rel, line, "doc-meta.commands must be a list"))
    else:
        for idx, cmd in enumerate(commands, start=1):
            if not isinstance(cmd, dict):
                issues.append(DocsIssue(rel, line, f"doc-meta.commands[{idx}] must be a mapping"))
                continue
            run = str(cmd.get("run", "")).strip()
            purpose = str(cmd.get("purpose", "")).strip()
            if not run:
                issues.append(DocsIssue(rel, line, f"doc-meta.commands[{idx}].run must be non-empty"))
            if not purpose:
                issues.append(DocsIssue(rel, line, f"doc-meta.commands[{idx}].purpose must be non-empty"))

    if not isinstance(examples, list):
        issues.append(DocsIssue(rel, line, "doc-meta.examples must be a list"))
    else:
        for idx, ex in enumerate(examples, start=1):
            if not isinstance(ex, dict):
                issues.append(DocsIssue(rel, line, f"doc-meta.examples[{idx}] must be a mapping"))
                continue
            ex_id = str(ex.get("id", "")).strip()
            runnable = ex.get("runnable")
            opt_out_reason = str(ex.get("opt_out_reason", "")).strip()
            if not _EXAMPLE_ID_RE.fullmatch(ex_id):
                issues.append(DocsIssue(rel, line, f"doc-meta.examples[{idx}].id must match EX-<...>"))
            if not isinstance(runnable, bool):
                issues.append(DocsIssue(rel, line, f"doc-meta.examples[{idx}].runnable must be bool"))
            if runnable is False and not opt_out_reason:
                issues.append(
                    DocsIssue(rel, line, f"doc-meta.examples[{idx}].opt_out_reason required when runnable=false")
                )

    if not isinstance(sections_required, list) or not sections_required:
        issues.append(DocsIssue(rel, line, "doc-meta.sections_required must be a non-empty list"))
    else:
        for item in sections_required:
            if not isinstance(item, str) or not item.strip():
                issues.append(DocsIssue(rel, line, "doc-meta.sections_required entries must be non-empty strings"))
                break
    return issues


def load_reference_manifest(repo_root: Path, rel_path: str) -> tuple[dict[str, Any], list[DocsIssue]]:
    issues: list[DocsIssue] = []
    try:
        path = resolve_contract_path(repo_root, rel_path, field="reference_manifest")
    except VirtualPathError:
        path = repo_root / rel_path.lstrip("/")
    if not path.exists():
        return {}, [DocsIssue(rel_path, 1, "missing reference manifest")]
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}, [DocsIssue(rel_path, 1, "reference manifest must be a mapping")]
    version = raw.get("version")
    if version != 1:
        issues.append(DocsIssue(rel_path, 1, "reference manifest version must be 1"))
    chapters = raw.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        issues.append(DocsIssue(rel_path, 1, "reference manifest chapters must be non-empty list"))
    else:
        for i, chapter in enumerate(chapters, start=1):
            if not isinstance(chapter, dict):
                issues.append(DocsIssue(rel_path, 1, f"chapters[{i}] must be mapping"))
                continue
            cpath = str(chapter.get("path", "")).strip()
            csummary = str(chapter.get("summary", "")).strip()
            if not cpath:
                issues.append(DocsIssue(rel_path, 1, f"chapters[{i}].path must be non-empty"))
            if not csummary:
                issues.append(DocsIssue(rel_path, 1, f"chapters[{i}].summary must be non-empty"))
    return raw, issues


def manifest_chapter_paths(manifest: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for item in manifest.get("chapters", []) or []:
        if isinstance(item, dict):
            rel = str(item.get("path", "")).strip()
            if rel:
                out.append(rel)
    return out


def render_reference_index(manifest: dict[str, Any]) -> str:
    lines = [
        "# Reference Index",
        "",
        "Canonical order for reference-manual chapters.",
        "",
        "## How To Use This Manual",
        "",
        "Read top-to-bottom for first adoption, then use chapter links as stable",
        "reference anchors during implementation and conformance review.",
        "",
    ]
    chapters = manifest.get("chapters", []) or []
    for idx, chapter in enumerate(chapters, start=1):
        if not isinstance(chapter, dict):
            continue
        rel = str(chapter.get("path", "")).strip()
        summary = str(chapter.get("summary", "")).strip()
        if rel and summary:
            lines.append(f"{idx}. `{rel}` - {summary}")
    lines.append("")
    return "\n".join(lines)


def _validate_shell_block(block_lines: list[str]) -> str | None:
    pending = ""
    pending_start = 0
    for i, raw in enumerate(block_lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if pending:
            line = f"{pending} {line}"
            pending = ""
        else:
            pending_start = i
        if line.startswith("$"):
            return f"shell line {i}: leading '$' prompt markers are not allowed"
        if line.endswith("\\"):
            pending = line[:-1].rstrip()
            continue
        try:
            shlex.split(line)
        except ValueError as exc:
            return f"shell line {i}: {exc}"
    if pending:
        return f"shell line {pending_start}: trailing line-continuation without command tail"
    return None


def _validate_python_block(block_lines: list[str]) -> str | None:
    try:
        compile("\n".join(block_lines), "<docs-python-example>", "exec")
    except SyntaxError as exc:
        return f"python syntax error: line {exc.lineno}: {exc.msg}"
    return None


def _has_example_opt_out(lines: list[str], start_line: int, end_line: int) -> bool:
    lo = max(0, start_line - 3)
    hi = min(len(lines), end_line + 4)
    for idx in range(lo, hi):
        m = _MARKER_RE.search(lines[idx])
        if m and m.group(1).strip():
            return True
    return False


def _default_instruction_sections() -> list[str]:
    return ["Purpose", "Inputs", "Outputs", "Failure Modes"]


def load_docs_meta_for_paths(
    repo_root: Path, rel_paths: list[str]
) -> tuple[dict[str, dict[str, Any]], list[DocsIssue], dict[str, int]]:
    metas: dict[str, dict[str, Any]] = {}
    meta_lines: dict[str, int] = {}
    issues: list[DocsIssue] = []
    for rel in rel_paths:
        try:
            path = resolve_contract_path(repo_root, rel, field="docs path")
        except VirtualPathError:
            path = repo_root / rel.lstrip("/")
        if not path.exists():
            issues.append(DocsIssue(rel, 1, "missing required docs file"))
            continue
        text = path.read_text(encoding="utf-8")
        meta, line = extract_doc_meta(text)
        if meta is None:
            issues.append(DocsIssue(rel, 1, "missing doc-meta block"))
            continue
        meta_lines[rel] = line
        issues.extend(validate_doc_meta(rel, meta, line=line))
        metas[rel] = meta
    return metas, issues, meta_lines


def check_token_ownership_unique(metas: dict[str, dict[str, Any]]) -> list[DocsIssue]:
    owners: dict[str, str] = {}
    issues: list[DocsIssue] = []
    for rel, meta in metas.items():
        for tok in meta.get("owns_tokens", []) or []:
            token = str(tok).strip()
            if not token:
                continue
            prev = owners.get(token)
            if prev is not None and prev != rel:
                issues.append(DocsIssue(rel, 1, f"token {token!r} already owned by {prev}"))
            else:
                owners[token] = rel
    return issues


def check_token_dependency_resolved(metas: dict[str, dict[str, Any]]) -> list[DocsIssue]:
    owners: dict[str, str] = {}
    issues: list[DocsIssue] = []
    owner_text: dict[str, str] = {}
    for rel, meta in metas.items():
        owner_text[rel] = (meta.get("__text__", "") or "")
        for tok in meta.get("owns_tokens", []) or []:
            token = str(tok).strip()
            if token and token not in owners:
                owners[token] = rel
    for rel, meta in metas.items():
        for tok in meta.get("requires_tokens", []) or []:
            token = str(tok).strip()
            if not token:
                continue
            owner_rel = owners.get(token)
            if owner_rel is None:
                issues.append(DocsIssue(rel, 1, f"required token {token!r} has no owner doc"))
                continue
            owner_doc_text = owner_text.get(owner_rel, "")
            if token not in owner_doc_text:
                issues.append(DocsIssue(rel, 1, f"owner doc {owner_rel} does not contain token {token!r}"))
    return issues


def check_instructions_complete(repo_root: Path, metas: dict[str, dict[str, Any]]) -> list[DocsIssue]:
    issues: list[DocsIssue] = []
    for rel, meta in metas.items():
        try:
            path = resolve_contract_path(repo_root, rel, field="docs path")
        except VirtualPathError:
            path = repo_root / rel.lstrip("/")
        text = path.read_text(encoding="utf-8")
        sections = meta.get("sections_required", []) or []
        want = [str(x).strip() for x in sections if str(x).strip()]
        if not want:
            want = _default_instruction_sections()
        lower = text.lower()
        missing = [tok for tok in want if tok.lower() not in lower]
        if missing:
            issues.append(DocsIssue(rel, 1, f"missing required section token(s): {', '.join(missing)}"))
    return issues


def check_command_examples_verified(repo_root: Path, rel_paths: list[str]) -> list[DocsIssue]:
    issues: list[DocsIssue] = []
    for rel in rel_paths:
        try:
            path = resolve_contract_path(repo_root, rel, field="docs path")
        except VirtualPathError:
            path = repo_root / rel.lstrip("/")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        blocks = _iter_fenced_blocks(text)
        for start, end, info, block_lines in blocks:
            err: str | None = None
            if "contract-spec" in info and ("yaml" in info or "yml" in info):
                try:
                    payload = yaml.safe_load("\n".join(block_lines))
                    if payload is None:
                        err = "empty contract-spec block"
                except Exception as exc:  # noqa: BLE001
                    err = f"yaml parse error: {exc}"
            elif info and info[0] in {"sh", "bash", "shell", "zsh"}:
                err = _validate_shell_block(block_lines)
            elif info and info[0] == "python":
                err = _validate_python_block(block_lines)
            if err and not _has_example_opt_out(lines, start, end):
                issues.append(DocsIssue(rel, start, f"invalid example block ({err})"))
    return issues


def check_example_id_uniqueness(metas: dict[str, dict[str, Any]]) -> list[DocsIssue]:
    seen: dict[str, str] = {}
    issues: list[DocsIssue] = []
    for rel, meta in metas.items():
        for ex in meta.get("examples", []) or []:
            if not isinstance(ex, dict):
                continue
            ex_id = str(ex.get("id", "")).strip()
            if not ex_id:
                continue
            prev = seen.get(ex_id)
            if prev is not None and prev != rel:
                issues.append(DocsIssue(rel, 1, f"duplicate example id {ex_id!r}; first declared in {prev}"))
            else:
                seen[ex_id] = rel
    return issues


def build_docs_graph(repo_root: Path, metas: dict[str, dict[str, Any]]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for rel, meta in sorted(metas.items()):
        nodes.append(
            {
                "path": rel,
                "doc_id": meta.get("doc_id"),
                "title": meta.get("title"),
                "status": meta.get("status"),
                "audience": meta.get("audience"),
            }
        )
        for tok in meta.get("owns_tokens", []) or []:
            edges.append({"from": rel, "to": str(tok), "kind": "owns_token"})
        for tok in meta.get("requires_tokens", []) or []:
            edges.append({"from": rel, "to": str(tok), "kind": "requires_token"})
        for cmd in meta.get("commands", []) or []:
            if not isinstance(cmd, dict):
                continue
            edges.append({"from": rel, "to": str(cmd.get("run", "")), "kind": "command"})
        for ex in meta.get("examples", []) or []:
            if not isinstance(ex, dict):
                continue
            edges.append({"from": rel, "to": str(ex.get("id", "")), "kind": "example"})
    return {
        "version": 1,
        "root": ".",
        "nodes": nodes,
        "edges": edges,
    }


def render_reference_coverage(repo_root: Path, metas: dict[str, dict[str, Any]]) -> str:
    total = len(metas)
    runnable = 0
    examples_total = 0
    for meta in metas.values():
        for ex in meta.get("examples", []) or []:
            if isinstance(ex, dict):
                examples_total += 1
                if ex.get("runnable") is True:
                    runnable += 1
    coverage = 0.0 if examples_total == 0 else runnable / examples_total
    lines = [
        "# Reference Coverage",
        "",
        f"- docs_count: {total}",
        f"- examples_total: {examples_total}",
        f"- examples_runnable: {runnable}",
        f"- runnable_example_ratio: {coverage:.4f}",
        "",
        "## Docs",
        "",
    ]
    for rel, meta in sorted(metas.items()):
        lines.append(f"- `{rel}` ({meta.get('doc_id', '')})")
    lines.append("")
    return "\n".join(lines)
