#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class LinkRef:
    target: str
    resolved: str | None
    missing: bool


def _classify(path: str) -> tuple[str, str, bool]:
    if path == "specs/current.md":
        return "spec.current", "specs", True
    if path == "specs/index.md":
        return "spec.root", "specs", True
    if path.startswith("specs/schema/"):
        return "spec.schema", "specs/schema", path.endswith("/index.md")
    if path.startswith("specs/contract/"):
        return "spec.contract", "specs/contract", path.endswith("/index.md")
    if path.startswith("specs/governance/"):
        return "spec.governance", "specs/governance", path.endswith("/index.md")
    if path.startswith("specs/libraries/"):
        return "spec.libraries", "specs/libraries", path.endswith("/index.md")
    if path.startswith("specs/impl/"):
        return "spec.impl", "specs/impl", path.endswith("/index.md")
    if path.startswith("docs/book/"):
        return "docs.book", "docs/book", path.endswith("/index.md")
    if path.startswith("docs/history/"):
        return "docs.history", "docs/history", False
    if path.startswith("docs/"):
        return "docs.other", "docs", False
    return "other", "other", False


def _resolve_link(root: Path, source: Path, target: str) -> tuple[str | None, bool]:
    if not target or target.startswith("#"):
        return None, False
    if target.startswith(("http://", "https://", "mailto:")):
        return None, False
    link_path = target.split("#", 1)[0].strip()
    if not link_path:
        return None, False
    if link_path.startswith("/"):
        resolved = (root / link_path.lstrip("/")).resolve()
    else:
        resolved = (source.parent / link_path).resolve()
    try:
        rel = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return None, True
    return rel, not resolved.exists()


def build_inventory(root: Path) -> dict[str, Any]:
    docs_root = root / "docs"
    files: list[dict[str, Any]] = []
    missing_links: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []
    all_md = sorted(p for p in docs_root.rglob("*.md") if p.is_file())
    for path in all_md:
        rel = path.relative_to(root).as_posix()
        section, owner, canonical = _classify(rel)
        text = path.read_text(encoding="utf-8")
        links: list[LinkRef] = []
        for match in _LINK_RE.finditer(text):
            raw = match.group(1).strip()
            resolved, missing = _resolve_link(root, path, raw)
            links.append(LinkRef(target=raw, resolved=resolved, missing=missing))
            if resolved:
                edges.append({"from": rel, "to": resolved})
            if missing:
                missing_links.append({"file": rel, "target": raw})
        files.append(
            {
                "path": rel,
                "section": section,
                "owner": owner,
                "canonical": canonical,
                "outgoing_links": [
                    {"target": link.target, "resolved": link.resolved, "missing": link.missing} for link in links
                ],
            }
        )

    return {
        "version": 1,
        "root": root.as_posix(),
        "summary": {
            "file_count": len(files),
            "canonical_count": sum(1 for f in files if f["canonical"]),
            "missing_link_count": len(missing_links),
        },
        "files": files,
        "link_graph": edges,
        "missing_links": missing_links,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build specs inventory and link graph.")
    parser.add_argument("--out", default=".artifacts/docs-inventory.json", help="output JSON path")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    payload = build_inventory(root)

    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
