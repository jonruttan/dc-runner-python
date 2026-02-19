from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import yaml

from spec_runner.virtual_paths import VirtualPathError, resolve_contract_path


REGISTRY_PATH = Path("specs/schema/docs_generator_registry_v1.yaml")


@dataclass(frozen=True)
class DocsGeneratorIssue:
    path: str
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}"


def resolve_virtual_path(repo_root: Path, raw: str, *, field: str) -> Path:
    try:
        return resolve_contract_path(repo_root, raw, field=field)
    except VirtualPathError:
        raw_path = Path(str(raw))
        if raw_path.is_absolute():
            return raw_path
        return repo_root / str(raw).lstrip("/")


def load_docs_generator_registry(repo_root: Path) -> tuple[dict[str, Any] | None, list[DocsGeneratorIssue]]:
    path = repo_root / REGISTRY_PATH
    if not path.exists():
        return None, [DocsGeneratorIssue(REGISTRY_PATH.as_posix(), "missing docs generator registry")]
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None, [DocsGeneratorIssue(REGISTRY_PATH.as_posix(), "registry must be a mapping")]
    issues: list[DocsGeneratorIssue] = []
    version = payload.get("version")
    if version != 1:
        issues.append(DocsGeneratorIssue(REGISTRY_PATH.as_posix(), "version must be 1"))
    surfaces = payload.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        issues.append(DocsGeneratorIssue(REGISTRY_PATH.as_posix(), "surfaces must be a non-empty list"))
        return None, issues
    seen: set[str] = set()
    for idx, raw in enumerate(surfaces):
        loc = f"{REGISTRY_PATH.as_posix()}:surfaces[{idx}]"
        if not isinstance(raw, dict):
            issues.append(DocsGeneratorIssue(loc, "surface entry must be a mapping"))
            continue
        sid = str(raw.get("surface_id", "")).strip()
        if not sid:
            issues.append(DocsGeneratorIssue(loc, "surface_id must be non-empty"))
            continue
        if sid in seen:
            issues.append(DocsGeneratorIssue(loc, f"duplicate surface_id: {sid}"))
        seen.add(sid)
        source_type = str(raw.get("source_type", "")).strip()
        if source_type not in {"manifest_yaml", "registry_yaml", "code_scan"}:
            issues.append(DocsGeneratorIssue(loc, "source_type must be manifest_yaml|registry_yaml|code_scan"))
        for key in ("inputs", "outputs", "owner_contract_docs", "determinism_hash_fields", "read_only_sections"):
            value = raw.get(key)
            if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
                issues.append(DocsGeneratorIssue(loc, f"{key} must be a list of non-empty strings"))
        gen = str(raw.get("generator", "")).strip()
        if not gen:
            issues.append(DocsGeneratorIssue(loc, "generator must be non-empty"))
        if not isinstance(raw.get("check_mode_supported"), bool):
            issues.append(DocsGeneratorIssue(loc, "check_mode_supported must be bool"))
        template_path = str(raw.get("template_path", "")).strip()
        if not template_path:
            issues.append(DocsGeneratorIssue(loc, "template_path must be non-empty"))
        output_mode = str(raw.get("output_mode", "")).strip()
        if output_mode not in {"markers", "full_file"}:
            issues.append(DocsGeneratorIssue(loc, "output_mode must be markers|full_file"))
        if output_mode == "markers":
            marker_surface_id = str(raw.get("marker_surface_id", "")).strip()
            if not marker_surface_id:
                issues.append(DocsGeneratorIssue(loc, "marker_surface_id is required when output_mode=markers"))
        data_sources = raw.get("data_sources")
        if not isinstance(data_sources, list) or not data_sources:
            issues.append(DocsGeneratorIssue(loc, "data_sources must be a non-empty list"))
        else:
            for src_idx, src in enumerate(data_sources):
                sloc = f"{loc}.data_sources[{src_idx}]"
                if not isinstance(src, dict):
                    issues.append(DocsGeneratorIssue(sloc, "data source entry must be a mapping"))
                    continue
                sid = str(src.get("id", "")).strip()
                if not sid:
                    issues.append(DocsGeneratorIssue(sloc, "id must be non-empty"))
                s_type = str(src.get("source_type", "")).strip()
                if s_type not in {"json_file", "yaml_file", "generated_artifact", "command_output"}:
                    issues.append(
                        DocsGeneratorIssue(
                            sloc,
                            "source_type must be json_file|yaml_file|generated_artifact|command_output",
                        )
                    )
                if s_type in {"json_file", "yaml_file", "generated_artifact"}:
                    path_value = str(src.get("path", "")).strip()
                    if not path_value:
                        issues.append(DocsGeneratorIssue(sloc, "path is required for file/artifact sources"))
                if s_type == "command_output":
                    cmd = src.get("command")
                    if not isinstance(cmd, list) or not cmd or any(not str(x).strip() for x in cmd):
                        issues.append(DocsGeneratorIssue(sloc, "command must be a non-empty list of args"))
    return (payload if not issues else None), issues


def generated_block_markers(surface_id: str) -> tuple[str, str]:
    return (f"<!-- GENERATED:START {surface_id} -->", f"<!-- GENERATED:END {surface_id} -->")


def replace_generated_block(text: str, *, surface_id: str, body: str) -> str:
    start, end = generated_block_markers(surface_id)
    if start not in text or end not in text:
        raise ValueError(f"missing generated markers for {surface_id}")
    i = text.index(start)
    j = text.index(end)
    if j < i:
        raise ValueError(f"invalid generated marker order for {surface_id}")
    head = text[: i + len(start)]
    tail = text[j:]
    block = "\n\n" + body.strip() + "\n"
    return head + block + tail


def parse_generated_block(text: str, *, surface_id: str) -> str:
    start, end = generated_block_markers(surface_id)
    if start not in text or end not in text:
        raise ValueError(f"missing generated markers for {surface_id}")
    i = text.index(start) + len(start)
    j = text.index(end)
    return text[i:j].strip()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
