from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

import yaml

from spec_runner.doc_parser import _iter_spec_test_blocks
from spec_runner.settings import SETTINGS, resolve_case_file_pattern

_CANONICAL_EXECUTABLE_TREES = (
    Path("specs/conformance/cases"),
    Path("specs/governance/cases"),
    Path("specs/impl"),
)


class ExternalCaseCodec(Protocol):
    def name(self) -> str: ...

    def can_load(self, path: Path) -> bool: ...

    def load_cases(self, path: Path) -> list[dict[str, Any]]: ...


class MarkdownYamlSpecCodec:
    def name(self) -> str:
        return "md"

    def can_load(self, path: Path) -> bool:
        return path.name.endswith(".md")

    def load_cases(self, path: Path) -> list[dict[str, Any]]:
        raw = path.read_text(encoding="utf-8")
        out: list[dict[str, Any]] = []
        for block in _iter_spec_test_blocks(raw):
            payload = yaml.safe_load(block) or {}
            if isinstance(payload, dict):
                tests = [payload]
            elif isinstance(payload, list):
                tests = payload
            else:
                raise TypeError(f"contract-spec block in {path} must be a mapping or a list of mappings")
            for t in tests:
                if not isinstance(t, dict):
                    raise TypeError(f"contract-spec block in {path} contains a non-mapping test")
                if "id" not in t or "type" not in t:
                    raise ValueError(f"contract-spec in {path} must include 'id' and 'type'")
                out.append(t)
        return out


class YamlSpecFileCodec:
    def name(self) -> str:
        return "yaml"

    def can_load(self, path: Path) -> bool:
        return path.name.endswith(".spec.yaml") or path.name.endswith(".spec.yml")

    def load_cases(self, path: Path) -> list[dict[str, Any]]:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(payload, dict):
            tests = [payload]
        elif isinstance(payload, list):
            tests = payload
        else:
            raise TypeError(f"spec file {path} must be a mapping or a list of mappings")
        out: list[dict[str, Any]] = []
        for t in tests:
            if not isinstance(t, dict):
                raise TypeError(f"spec file {path} contains a non-mapping test")
            if "id" not in t or "type" not in t:
                raise ValueError(f"spec in {path} must include 'id' and 'type'")
            out.append(t)
        return out


class JsonSpecFileCodec:
    def name(self) -> str:
        return "json"

    def can_load(self, path: Path) -> bool:
        return path.name.endswith(".spec.json")

    def load_cases(self, path: Path) -> list[dict[str, Any]]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            tests = [payload]
        elif isinstance(payload, list):
            tests = payload
        else:
            raise TypeError(f"spec file {path} must be a mapping or a list of mappings")
        out: list[dict[str, Any]] = []
        for t in tests:
            if not isinstance(t, dict):
                raise TypeError(f"spec file {path} contains a non-mapping test")
            if "id" not in t or "type" not in t:
                raise ValueError(f"spec in {path} must include 'id' and 'type'")
            out.append(t)
        return out


def default_codecs() -> dict[str, ExternalCaseCodec]:
    return {
        "md": MarkdownYamlSpecCodec(),
        "yaml": YamlSpecFileCodec(),
        "json": JsonSpecFileCodec(),
    }


def _patterns_for_format(fmt: str, *, md_pattern: str | None = None) -> list[str]:
    if fmt == "md":
        return [resolve_case_file_pattern(md_pattern or SETTINGS.case.default_file_pattern)]
    if fmt == "yaml":
        return ["*.spec.yaml", "*.spec.yml"]
    if fmt == "json":
        return ["*.spec.json"]
    raise ValueError(f"unknown format: {fmt}")


def discover_case_files(
    root: Path,
    *,
    formats: set[str] | None = None,
    md_pattern: str | None = None,
) -> list[tuple[Path, str]]:
    fmts = formats or {"md"}
    codecs = default_codecs()
    for f in fmts:
        if f not in codecs:
            raise ValueError(f"unsupported format: {f}")
    if any(fmt != "md" for fmt in fmts):
        root_resolved = root.resolve()
        for tree in _CANONICAL_EXECUTABLE_TREES:
            tree_resolved = tree.resolve()
            try:
                root_resolved.relative_to(tree_resolved)
            except ValueError:
                continue
            raise ValueError(
                "canonical executable case trees are markdown-only; "
                "non-md case formats are not allowed"
            )

    out: list[tuple[Path, str]] = []
    if root.is_file():
        for fmt in fmts:
            c = codecs[fmt]
            if c.can_load(root):
                out.append((root, fmt))
                return out
        raise RuntimeError(f"cases path is a file but does not match enabled formats: {root}")

    for fmt in sorted(fmts):
        for pattern in _patterns_for_format(fmt, md_pattern=md_pattern):
            for p in sorted(root.rglob(pattern)):
                if p.is_file() and codecs[fmt].can_load(p):
                    out.append((p, fmt))
    return out


def load_external_cases(
    root: Path,
    *,
    formats: set[str] | None = None,
    md_pattern: str | None = None,
) -> list[tuple[Path, dict[str, Any]]]:
    codecs = default_codecs()
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for path, fmt in discover_case_files(root, formats=formats, md_pattern=md_pattern):
        codec = codecs[fmt]
        for case in codec.load_cases(path):
            loaded.append((path, case))
    return loaded
