from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


class VirtualPathError(ValueError):
    pass


_EXTERNAL_RE = re.compile(r"^external://([^/]+)/(.+)$")
_DRIVE_ABS_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class ExternalRef:
    raw: str
    provider: str
    ref_id: str


def contract_root_for(anchor_path: Path) -> Path:
    """
    Resolve contract root from an anchor path.

    If a .git root is found while walking parents, use it. Otherwise use the
    anchor directory (for files) or the path itself (for dirs).
    """
    p = anchor_path.resolve()
    cur = p if p.is_dir() else p.parent
    for candidate in (cur, *cur.parents):
        if (candidate / ".git").exists():
            return candidate
    if p.is_file():
        marker_dirs = {
            "cases",
            "spec",
            "conformance",
            "governance",
            "libraries",
            "libs",
            "contract",
            "schema",
            "book",
        }
        if cur.name.lower() in marker_dirs:
            parent = cur.parent
            return parent if parent != cur else cur
    return cur


def parse_external_ref(raw: str) -> ExternalRef | None:
    s = str(raw).strip()
    m = _EXTERNAL_RE.match(s)
    if not m:
        return None
    provider = m.group(1).strip()
    ref_id = m.group(2).strip()
    if not provider or not ref_id:
        raise VirtualPathError(f"invalid external ref: {raw}")
    return ExternalRef(raw=s, provider=provider, ref_id=ref_id)


def normalize_contract_path(raw: str, *, field: str) -> str:
    s = str(raw).strip()
    if not s:
        raise VirtualPathError(f"{field} must be a non-empty path")
    if parse_external_ref(s) is not None:
        raise VirtualPathError(f"{field} must be a contract path, not external:// reference")

    if _DRIVE_ABS_RE.match(s):
        raise VirtualPathError(f"{field} must not use OS-absolute drive paths")
    if s.startswith("\\\\"):
        raise VirtualPathError(f"{field} must not use UNC absolute paths")

    s = s.replace("\\", "/")
    if not s.startswith("/"):
        s = "/" + s

    parts: list[str] = []
    for token in s.split("/"):
        part = token.strip()
        if not part or part == ".":
            continue
        if part == "..":
            if not parts:
                raise VirtualPathError(f"{field} escapes contract root")
            parts.pop()
            continue
        parts.append(part)
    return "/" + "/".join(parts)


def resolve_contract_path(contract_root: Path, raw: str, *, field: str) -> Path:
    root = contract_root.resolve()
    normalized = normalize_contract_path(raw, field=field)
    candidate = (root / normalized.lstrip("/")).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise VirtualPathError(f"{field} escapes contract root") from exc
    return candidate
