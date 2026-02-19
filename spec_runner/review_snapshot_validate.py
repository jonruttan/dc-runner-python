from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Scope Notes",
    "Command Execution Log",
    "Findings",
    "Synthesis",
    "Spec Candidates (YAML)",
    "Classification Labels",
    "Reject / Defer List",
    "Raw Output",
)
REQUIRED_METADATA_FIELDS: tuple[str, ...] = (
    "Date:",
    "Model:",
    "Prompt:",
    "Prompt revision:",
    "Repo revision:",
    "Contract baseline refs:",
    "Runner lane:",
)

COMMAND_LOG_HEADER = ["command", "status", "exit_code", "stdout_stderr_summary"]
FINDINGS_HEADER = [
    "Severity",
    "Verified/Hypothesis",
    "File:Line",
    "What",
    "Why",
    "When",
    "Proposed fix",
]

REQUIRED_CANDIDATE_KEYS: tuple[str, ...] = (
    "id",
    "title",
    "type",
    "class",
    "target_area",
    "acceptance_criteria",
    "affected_paths",
    "risk",
)


def _section_map(md: str) -> tuple[list[str], dict[str, str]]:
    headings: list[str] = []
    offsets: list[int] = []
    lines = md.splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("## "):
            headings.append(line[3:].strip())
            offsets.append(idx)
    sections: dict[str, str] = {}
    for i, heading in enumerate(headings):
        start = offsets[i] + 1
        end = offsets[i + 1] if i + 1 < len(offsets) else len(lines)
        sections[heading] = "\n".join(lines[start:end]).strip()
    return headings, sections


def _extract_first_table_header(section_text: str) -> list[str] | None:
    for line in section_text.splitlines():
        raw = line.strip()
        if not raw.startswith("|"):
            continue
        cols = [x.strip() for x in raw.strip("|").split("|")]
        if len(cols) >= 2:
            return cols
    return None


def _extract_first_yaml_block(section_text: str) -> str | None:
    in_yaml = False
    buf: list[str] = []
    for line in section_text.splitlines():
        s = line.strip()
        if not in_yaml and s.startswith("```yaml"):
            in_yaml = True
            buf = []
            continue
        if in_yaml and s == "```":
            return "\n".join(buf).strip()
        if in_yaml:
            buf.append(line)
    return None


def parse_classification_labels(section_text: str) -> dict[str, str]:
    labels: dict[str, str] = {}
    pattern = re.compile(r"^\s*-\s*`?([^`]+?)`?\s*:\s*(behavior|docs|tooling)\s*$", re.IGNORECASE)
    for line in section_text.splitlines():
        m = pattern.match(line)
        if not m:
            continue
        labels[m.group(1).strip()] = m.group(2).lower()
    return labels


def parse_spec_candidates(section_text: str) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    block = _extract_first_yaml_block(section_text)
    if not block:
        return [], ["section 'Spec Candidates (YAML)' must include a fenced ```yaml block"]
    try:
        payload = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        return [], [f"spec candidates yaml is invalid ({exc})"]
    if not isinstance(payload, list):
        return [], ["spec candidates yaml root must be a list"]

    out: list[dict[str, Any]] = []
    for idx, item in enumerate(payload):
        loc = f"Spec Candidates (YAML)[{idx}]"
        if not isinstance(item, dict):
            errors.append(f"{loc} must be a mapping")
            continue
        missing = [k for k in REQUIRED_CANDIDATE_KEYS if k not in item]
        if missing:
            errors.append(f"{loc} missing keys: {', '.join(missing)}")
            continue
        criteria = item.get("acceptance_criteria")
        paths = item.get("affected_paths")
        if not isinstance(criteria, list) or not criteria or any(not isinstance(x, str) or not x.strip() for x in criteria):
            errors.append(f"{loc}.acceptance_criteria must be a non-empty list of non-empty strings")
        if not isinstance(paths, list) or not paths or any(not isinstance(x, str) or not x.strip() for x in paths):
            errors.append(f"{loc}.affected_paths must be a non-empty list of non-empty strings")
        out.append(dict(item))
    return out, errors


def validate_review_snapshot_text(md: str, *, source: str = "<snapshot>") -> list[str]:
    violations: list[str] = []
    for token in REQUIRED_METADATA_FIELDS:
        if token not in md:
            violations.append(f"{source}: missing required metadata token '{token}'")

    headings, sections = _section_map(md)

    idx = -1
    for section in REQUIRED_SECTIONS:
        if section not in sections:
            violations.append(f"{source}: missing required section '## {section}'")
            continue
        next_idx = headings.index(section)
        if next_idx <= idx:
            violations.append(f"{source}: required section order violation at '## {section}'")
        idx = next_idx

    cmd_section = sections.get("Command Execution Log")
    if cmd_section is not None:
        header = _extract_first_table_header(cmd_section)
        if header != COMMAND_LOG_HEADER:
            violations.append(
                f"{source}: Command Execution Log header must be: {' | '.join(COMMAND_LOG_HEADER)}"
            )

    findings_section = sections.get("Findings")
    if findings_section is not None:
        header = _extract_first_table_header(findings_section)
        if header != FINDINGS_HEADER:
            violations.append(
                f"{source}: Findings header must be: {' | '.join(FINDINGS_HEADER)}"
            )

    candidates_section = sections.get("Spec Candidates (YAML)")
    candidates: list[dict[str, Any]] = []
    if candidates_section is not None:
        candidates, errs = parse_spec_candidates(candidates_section)
        violations.extend(f"{source}: {err}" for err in errs)

    labels_section = sections.get("Classification Labels")
    if labels_section is not None:
        labels = parse_classification_labels(labels_section)
        for candidate in candidates:
            cid = str(candidate.get("id", "")).strip()
            if not cid:
                continue
            if cid not in labels:
                violations.append(f"{source}: Classification Labels missing id '{cid}'")

    return violations


def validate_review_snapshot(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path.as_posix()}: unable to read snapshot ({exc})"]
    return validate_review_snapshot_text(text, source=path.as_posix())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate docs/reviews snapshot structure and candidate schema.")
    ap.add_argument("--snapshot", required=True, help="Path to review snapshot markdown")
    ns = ap.parse_args(argv)

    path = Path(ns.snapshot)
    if not path.exists() or not path.is_file():
        print(f"ERROR: snapshot does not exist: {path}", file=sys.stderr)
        return 2

    violations = validate_review_snapshot(path)
    if violations:
        for line in violations:
            print(f"ERROR: {line}", file=sys.stderr)
        return 1
    print(f"OK: review snapshot contract valid ({path.as_posix()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
