#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[3]
PROFILE_PATH = ROOT / "specs/schema/docs_layout_profile_v1.yaml"


def _load_profile(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: profile must be a mapping")
    return payload


def _to_rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


def _from_contract_path(root: Path, raw: str) -> Path:
    return root / raw.lstrip("/")


def _all_docs_files(root: Path) -> list[Path]:
    docs = root / "docs"
    if not docs.exists():
        return []
    return sorted(p for p in docs.rglob("*") if p.is_file())


def _check_layout(profile: dict, root: Path) -> list[str]:
    issues: list[str] = []
    index_name = str(profile.get("index_filename", "index.md")).strip() or "index.md"

    for raw in profile.get("canonical_roots", []):
        p = _from_contract_path(root, str(raw))
        if not p.exists() or not p.is_dir():
            issues.append(f"{str(raw).lstrip('/')}:1: DOCS_LAYOUT_CANONICAL_TREES_REQUIRED: missing canonical root")

    for raw in profile.get("forbidden_roots", []):
        p = _from_contract_path(root, str(raw))
        if p.exists():
            issues.append(f"{str(raw).lstrip('/')}:1: DOCS_REVIEWS_NAMESPACE_ACTIVE_REQUIRED: forbidden root exists")

    required_index_dirs = profile.get("required_index_dirs", [])
    for raw in required_index_dirs:
        d = _from_contract_path(root, str(raw))
        if not d.exists() or not d.is_dir():
            issues.append(f"{str(raw).lstrip('/')}:1: DOCS_INDEX_FILENAME_INDEX_MD_REQUIRED: missing index directory")
            continue
        index_path = d / index_name
        if not index_path.exists():
            issues.append(f"{_to_rel(root, index_path)}:1: DOCS_INDEX_FILENAME_INDEX_MD_REQUIRED: missing index.md")

    forbidden = {str(x).strip() for x in profile.get("forbidden_filenames", []) if str(x).strip()}
    for p in _all_docs_files(root):
        rel = _to_rel(root, p)
        if p.name in forbidden:
            rule = "DOCS_NO_OS_ARTIFACT_FILES_TRACKED" if p.name == ".DS_Store" else "DOCS_INDEX_FILENAME_INDEX_MD_REQUIRED"
            issues.append(f"{rel}:1: {rule}: forbidden filename {p.name}")

        if any(c.isupper() for c in rel):
            issues.append(f"{rel}:1: DOCS_FILENAME_POLICY_REQUIRED: uppercase characters are forbidden")
        if " " in rel:
            issues.append(f"{rel}:1: DOCS_FILENAME_POLICY_REQUIRED: spaces are forbidden")

        if not re.fullmatch(r"[a-z0-9_./-]+", rel):
            issues.append(f"{rel}:1: DOCS_FILENAME_POLICY_REQUIRED: unsupported path characters")

    return issues


def _rewrite_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text
    for old, new in replacements:
        updated = updated.replace(old, new)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def _write_layout(profile: dict, root: Path) -> list[str]:
    issues: list[str] = []
    replacements = [
        ("docs/book/README.md", "docs/book/index.md"),
        ("specs/README.md", "specs/index.md"),
        ("specs/contract/README.md", "specs/contract/index.md"),
        ("specs/governance/README.md", "specs/governance/index.md"),
        ("specs/conformance/README.md", "specs/conformance/index.md"),
        ("specs/conformance/cases/README.md", "specs/conformance/cases/index.md"),
        ("specs/impl/php/cases/README.md", "specs/impl/php/cases/index.md"),
    ]

    for p in _all_docs_files(root):
        if p.suffix in {".md", ".yaml", ".yml", ".json", ".txt"}:
            _rewrite_file(p, replacements)

    from_to = [
        ("docs/book/README.md", "docs/book/index.md"),
        ("specs/README.md", "specs/index.md"),
        ("specs/contract/README.md", "specs/contract/index.md"),
        ("specs/governance/README.md", "specs/governance/index.md"),
        ("specs/conformance/README.md", "specs/conformance/index.md"),
        ("specs/conformance/cases/README.md", "specs/conformance/cases/index.md"),
        ("specs/impl/php/cases/README.md", "specs/impl/php/cases/index.md"),
    ]
    for old_rel, new_rel in from_to:
        old = root / old_rel
        new = root / new_rel
        if old.exists():
            new.parent.mkdir(parents=True, exist_ok=True)
            old.rename(new)

    for p in _all_docs_files(root):
        if p.name == ".DS_Store":
            p.unlink()

    issues.extend(_check_layout(profile, root))
    return issues


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Normalize docs layout and naming conventions.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    ap.add_argument("--profile", default=str(PROFILE_PATH))
    ns = ap.parse_args(argv)

    try:
        profile = _load_profile(Path(ns.profile))
    except Exception as exc:  # noqa: BLE001
        print(f"{Path(ns.profile).as_posix()}:1: NORMALIZATION_PROFILE: {exc}")
        return 1

    if ns.write:
        issues = _write_layout(profile, ROOT)
    else:
        issues = _check_layout(profile, ROOT)

    if issues:
        for issue in sorted(issues):
            print(issue)
        return 1
    print("OK: docs layout normalization passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
