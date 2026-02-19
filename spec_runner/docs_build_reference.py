#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from spec_runner.docs_quality import (
    DocsIssue,
    build_docs_graph,
    load_docs_meta_for_paths,
    load_reference_manifest,
    manifest_chapter_paths,
    render_reference_coverage,
    render_reference_index,
)
from spec_runner.virtual_paths import VirtualPathError, resolve_contract_path


def _render_issues(issues: list[DocsIssue]) -> None:
    for issue in issues:
        print(issue.render())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Build and verify generated reference-doc artifacts from manifest + doc-meta."
    )
    ap.add_argument("--manifest", default="docs/book/reference_manifest.yaml")
    ap.add_argument("--index-out", default="docs/book/reference_index.md")
    ap.add_argument("--coverage-out", default="docs/book/reference_coverage.md")
    ap.add_argument("--graph-out", default="docs/book/docs_graph.json")
    ap.add_argument("--check", action="store_true", help="Verify generated files are up-to-date")
    ns = ap.parse_args(argv)

    root = Path.cwd()
    manifest, issues = load_reference_manifest(root, str(ns.manifest))
    if issues:
        _render_issues(issues)
        return 1

    docs = manifest_chapter_paths(manifest)
    metas, meta_issues, _meta_lines = load_docs_meta_for_paths(root, docs)
    if meta_issues:
        _render_issues(meta_issues)
        return 1
    for rel in docs:
        if rel in metas:
            try:
                p = resolve_contract_path(root, rel, field="reference_manifest chapter path")
            except VirtualPathError:
                p = root / rel.lstrip("/")
            metas[rel]["__text__"] = p.read_text(encoding="utf-8")

    index_text = render_reference_index(manifest)
    coverage_text = render_reference_coverage(root, metas)
    graph = build_docs_graph(root, metas)
    graph_text = json.dumps(graph, indent=2, sort_keys=True) + "\n"

    try:
        index_path = resolve_contract_path(root, str(ns.index_out), field="index_out")
    except VirtualPathError:
        index_path = root / str(ns.index_out).lstrip("/")
    try:
        coverage_path = resolve_contract_path(root, str(ns.coverage_out), field="coverage_out")
    except VirtualPathError:
        coverage_path = root / str(ns.coverage_out).lstrip("/")
    try:
        graph_path = resolve_contract_path(root, str(ns.graph_out), field="graph_out")
    except VirtualPathError:
        graph_path = root / str(ns.graph_out).lstrip("/")

    if ns.check:
        bad = False
        if not index_path.exists() or index_path.read_text(encoding="utf-8") != index_text:
            print(f"{ns.index_out}: generated content out of date")
            bad = True
        if not coverage_path.exists() or coverage_path.read_text(encoding="utf-8") != coverage_text:
            print(f"{ns.coverage_out}: generated content out of date")
            bad = True
        if not graph_path.exists() or graph_path.read_text(encoding="utf-8") != graph_text:
            print(f"{ns.graph_out}: generated content out of date")
            bad = True
        return 1 if bad else 0

    index_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(index_text, encoding="utf-8")
    coverage_path.write_text(coverage_text, encoding="utf-8")
    graph_path.write_text(graph_text, encoding="utf-8")
    print(f"wrote {ns.index_out}")
    print(f"wrote {ns.coverage_out}")
    print(f"wrote {ns.graph_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
