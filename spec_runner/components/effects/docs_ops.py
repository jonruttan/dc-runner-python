from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import yaml

from spec_runner.docs_generators import (
    load_docs_generator_registry,
    replace_generated_block,
    resolve_virtual_path,
)
from spec_runner.docs_template_engine import render_moustache


def resolve_docs_generate_harness_config(case_harness: dict[str, Any]) -> dict[str, Any]:
    cfg = case_harness.get("docs_generate")
    if not isinstance(cfg, dict):
        raise TypeError("docs.generate requires harness.docs_generate mapping")
    return cfg


def required_non_empty_string(cfg: dict[str, Any], key: str) -> str:
    value = str(cfg.get(key, "")).strip()
    if not value:
        raise ValueError(f"harness.docs_generate.{key} must be a non-empty string")
    return value


def mode_for_run(cfg: dict[str, Any], *, env: dict[str, str]) -> str:
    mode = str(cfg.get("mode", "")).strip().lower()
    if not mode:
        raise ValueError("harness.docs_generate.mode must be provided")
    override = str(env.get("SPEC_DOCS_GENERATE_MODE", "")).strip().lower()
    if override:
        mode = override
    if mode not in {"write", "check"}:
        raise ValueError("harness.docs_generate.mode must be write|check")
    return mode


def surface_by_id(registry: dict[str, Any], surface_id: str) -> dict[str, Any]:
    for raw in registry.get("surfaces") or []:
        if not isinstance(raw, dict):
            continue
        if str(raw.get("surface_id", "")).strip() == surface_id:
            return raw
    raise ValueError(f"unknown docs generator surface_id: {surface_id}")


def _subprocess_run(
    *,
    command: list[str],
    root: Path,
    profiler: object | None = None,
    phase: str,
) -> subprocess.CompletedProcess[str]:
    if profiler is not None and hasattr(profiler, "subprocess_run"):
        return profiler.subprocess_run(
            command=command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            phase=phase,
        )
    return subprocess.run(command, cwd=root, check=False, capture_output=True, text=True)


def load_source(root: Path, raw: dict[str, Any], *, profiler: object | None = None) -> tuple[str, Any]:
    source_id = str(raw.get("id", "")).strip()
    source_type = str(raw.get("source_type", "")).strip()
    if not source_id:
        raise ValueError("docs_generate.data_sources[*].id must be non-empty")
    if source_type in {"json_file", "yaml_file", "generated_artifact"}:
        path_raw = str(raw.get("path", "")).strip()
        if not path_raw:
            raise ValueError(f"docs_generate.data_sources[{source_id}].path is required")
        path = resolve_virtual_path(root, path_raw, field=f"docs_generate.data_sources.{source_id}.path")
        if not path.exists():
            raise ValueError(f"docs_generate data source path missing: {path_raw}")
        text = path.read_text(encoding="utf-8")
        if source_type == "json_file" or path.suffix.lower() == ".json":
            return source_id, _decorate_source(source_id, json.loads(text))
        if source_type == "yaml_file" or path.suffix.lower() in {".yaml", ".yml"}:
            return source_id, _decorate_source(source_id, yaml.safe_load(text))
        return source_id, _decorate_source(source_id, text)
    if source_type == "command_output":
        command = raw.get("command")
        if not isinstance(command, list) or not command or any(not str(x).strip() for x in command):
            raise ValueError(f"docs_generate.data_sources[{source_id}].command must be a non-empty list")
        cp = _subprocess_run(
            command=[str(x) for x in command],
            root=root,
            profiler=profiler,
            phase=f"docs.data_source.{source_id}",
        )
        if cp.returncode != 0:
            out = ((cp.stdout or "") + "\n" + (cp.stderr or "")).strip()
            raise RuntimeError(out or f"docs_generate command_output failed for source {source_id}")
        out_fmt = str(raw.get("format", "text")).strip().lower() or "text"
        if out_fmt == "json":
            return source_id, _decorate_source(source_id, json.loads(cp.stdout or "{}"))
        if out_fmt == "yaml":
            return source_id, _decorate_source(source_id, yaml.safe_load(cp.stdout or ""))
        return source_id, _decorate_source(source_id, cp.stdout or "")
    raise ValueError(
        f"docs_generate.data_sources[{source_id}].source_type must be json_file|yaml_file|generated_artifact|command_output"
    )


def _missing_generated_artifact_paths(root: Path, data_sources: list[dict[str, Any]]) -> list[str]:
    missing: list[str] = []
    for raw in data_sources:
        if not isinstance(raw, dict):
            continue
        source_type = str(raw.get("source_type", "")).strip()
        if source_type != "generated_artifact":
            continue
        path_raw = str(raw.get("path", "")).strip()
        if not path_raw:
            continue
        path = resolve_virtual_path(root, path_raw, field="harness.docs_generate.data_sources.path")
        if not path.exists():
            missing.append(path_raw)
    return missing


def _render_md_list(values: Any) -> str:
    if not isinstance(values, list) or not values:
        return "-"
    return ", ".join(f"`{str(x)}`" for x in values)


def _decorate_source(source_id: str, payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    if source_id == "policy":
        rows = payload.get("rules")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                lifecycle = "active"
                if str(row.get("removed_in", "")).strip():
                    lifecycle = "removed"
                elif str(row.get("deprecated_in", "")).strip():
                    lifecycle = "deprecated"
                row["lifecycle"] = lifecycle
    if source_id == "harness":
        rows = payload.get("type_profiles")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                row["required_top_level_md"] = _render_md_list(row.get("required_top_level"))
                row["allowed_top_level_extra_md"] = _render_md_list(row.get("allowed_top_level_extra"))
    if source_id == "schema":
        rows = payload.get("type_profiles")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                row["required_top_level_md"] = _render_md_list(row.get("required_top_level"))
    if source_id == "metrics":
        rows = payload.get("baselines")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                row["summary_field_count"] = len(row.get("summary_fields") or [])
    return payload


def render_output(
    *,
    output_mode: str,
    output_path: Path,
    marker_surface_id: str | None,
    rendered: str,
    mode: str,
) -> tuple[bool, str]:
    if output_mode == "full_file":
        existing = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        if mode == "check":
            if existing != rendered:
                raise AssertionError(f"{output_path}: generated content out of date")
            return False, existing
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        return existing != rendered, rendered
    if output_mode == "markers":
        marker_id = str(marker_surface_id or "").strip()
        if not marker_id:
            raise ValueError("harness.docs_generate.marker_surface_id is required when output_mode=markers")
        if not output_path.exists():
            raise ValueError(f"docs.generate marker output missing: {output_path}")
        existing = output_path.read_text(encoding="utf-8")
        updated = replace_generated_block(existing, surface_id=marker_id, body=rendered)
        if mode == "check":
            if existing != updated:
                raise AssertionError(f"{output_path}: generated content out of date")
            return False, existing
        output_path.write_text(updated, encoding="utf-8")
        return existing != updated, updated
    raise ValueError("harness.docs_generate.output_mode must be markers|full_file")


def run_docs_generation_op(
    *,
    root: Path,
    cfg: dict[str, Any],
    runtime_env: dict[str, str],
    profiler: object | None = None,
) -> dict[str, Any]:
    mode = mode_for_run(cfg, env=runtime_env)
    surface_id = required_non_empty_string(cfg, "surface_id")
    output_mode = required_non_empty_string(cfg, "output_mode")
    template_path_raw = required_non_empty_string(cfg, "template_path")
    output_path_raw = required_non_empty_string(cfg, "output_path")
    strict = bool(cfg.get("strict", True))

    registry, issues = load_docs_generator_registry(root)
    if registry is None:
        message = "; ".join(x.render() for x in issues) if issues else "docs generator registry invalid"
        raise ValueError(message)
    _ = surface_by_id(registry, surface_id)

    template_path = resolve_virtual_path(root, template_path_raw, field="harness.docs_generate.template_path")
    output_path = resolve_virtual_path(root, output_path_raw, field="harness.docs_generate.output_path")
    if not template_path.exists():
        raise ValueError(f"docs.generate template path missing: {template_path_raw}")
    template_text = template_path.read_text(encoding="utf-8")

    data_sources = cfg.get("data_sources")
    if not isinstance(data_sources, list) or not data_sources:
        raise ValueError("harness.docs_generate.data_sources must be a non-empty list")
    sources: dict[str, Any] = {}
    for idx, raw in enumerate(data_sources):
        if not isinstance(raw, dict):
            raise TypeError(f"harness.docs_generate.data_sources[{idx}] must be a mapping")
        sid, payload = load_source(root, raw, profiler=profiler)
        sources[sid] = payload
    context: dict[str, Any] = {"surface_id": surface_id, "mode": mode, "output_mode": output_mode, "sources": sources}
    for sid, payload in sources.items():
        context[sid] = payload
    rendered = render_moustache(template_text, context, strict=strict)
    changed, output_text = render_output(
        output_mode=output_mode,
        output_path=output_path,
        marker_surface_id=cfg.get("marker_surface_id"),
        rendered=rendered,
        mode=mode,
    )
    return {
        "mode": mode,
        "surface_id": surface_id,
        "output_mode": output_mode,
        "changed": bool(changed),
        "output_text": output_text,
        "template_path": template_path,
        "output_path": output_path,
        "data_source_ids": sorted(sources.keys()),
    }
