from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml
from spec_runner.settings import SETTINGS, resolve_case_file_pattern


@dataclass(frozen=True)
class SpecDocTest:
    doc_path: Path
    test: dict[str, Any]


def _is_spec_test_opening_fence(line: str) -> tuple[str, int] | None:
    # Markdown-style fences: 3+ of the same fence char, optional info string.
    stripped = line.lstrip(" \t")
    if not stripped:
        return None
    if stripped[0] not in ("`", "~"):
        return None
    fence_char = stripped[0]
    i = 0
    while i < len(stripped) and stripped[i] == fence_char:
        i += 1
    if i < 3:
        return None

    info = stripped[i:].strip()
    if not info:
        return None
    tokens = {tok.lower() for tok in info.split()}
    if "contract-spec" not in tokens:
        return None
    if "yaml" not in tokens and "yml" not in tokens:
        return None
    return fence_char, i


def _is_closing_fence(line: str, *, fence_char: str, min_len: int) -> bool:
    stripped = line.lstrip(" \t").rstrip()
    if not stripped or stripped[0] != fence_char:
        return False
    i = 0
    while i < len(stripped) and stripped[i] == fence_char:
        i += 1
    # Closing fence must contain only fence chars and be at least opening length.
    return i >= min_len and i == len(stripped)


def _iter_spec_test_blocks(raw: str) -> Iterator[str]:
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        opening = _is_spec_test_opening_fence(lines[i])
        if not opening:
            i += 1
            continue
        fence_char, fence_len = opening
        i += 1
        block_lines: list[str] = []
        while i < len(lines):
            if _is_closing_fence(lines[i], fence_char=fence_char, min_len=fence_len):
                break
            block_lines.append(lines[i])
            i += 1
        if i < len(lines):
            yield "\n".join(block_lines)
        i += 1


def iter_spec_doc_tests(spec_dir: Path, *, file_pattern: str | None = None) -> Iterator[SpecDocTest]:
    pattern = resolve_case_file_pattern(file_pattern or SETTINGS.case.default_file_pattern)
    for p in sorted(spec_dir.glob(pattern)):
        raw = p.read_text(encoding="utf-8")
        for block in _iter_spec_test_blocks(raw):
            payload = yaml.safe_load(block) or {}
            if isinstance(payload, dict):
                tests = [payload]
            elif isinstance(payload, list):
                tests = payload
            else:
                raise TypeError(f"contract-spec block in {p} must be a mapping or a list of mappings")

            for t in tests:
                if not isinstance(t, dict):
                    raise TypeError(f"contract-spec block in {p} contains a non-mapping test")
                if "id" not in t or "type" not in t:
                    raise ValueError(f"contract-spec in {p} must include 'id' and 'type'")
                yield SpecDocTest(doc_path=p, test=t)
