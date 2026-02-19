#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path


def _git_sha(short: bool = False) -> str:
    args = ["git", "rev-parse"]
    if short:
        args.append("--short")
    args.append("HEAD")
    cp = subprocess.run(args, check=True, capture_output=True, text=True)
    return cp.stdout.strip()


def _slug(value: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return s or "review"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Create a dated review snapshot markdown file with prompt/repo revisions prefilled.",
    )
    ap.add_argument(
        "--prompt",
        default="docs/reviews/prompts/adoption_7_personas.md",
        help="Path to prompt file used for the review",
    )
    ap.add_argument(
        "--label",
        default="persona_review",
        help="Label used in snapshot filename",
    )
    ap.add_argument(
        "--model",
        default="<fill in>",
        help="Model name to prefill",
    )
    ap.add_argument(
        "--out-dir",
        default="docs/reviews/snapshots",
        help="Directory where snapshot file is written",
    )
    ns = ap.parse_args(argv)

    today = dt.date.today().isoformat()
    prompt_path = Path(ns.prompt)
    out_dir = Path(ns.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prompt_sha = _git_sha(short=True)
    repo_sha = _git_sha(short=True)
    stem = f"{today}_{_slug(ns.label)}"
    out_path = out_dir / f"{stem}.md"
    if out_path.exists():
        i = 2
        while True:
            alt = out_dir / f"{stem}_{i}.md"
            if not alt.exists():
                out_path = alt
                break
            i += 1

    body = (
        f"# Review Snapshot\n\n"
        f"Date: {today}\n"
        f"Model: {ns.model}\n"
        f"Prompt: `{prompt_path.as_posix()}`\n"
        f"Prompt revision: {prompt_sha}\n"
        f"Repo revision: {repo_sha}\n"
        "Contract baseline refs:\n"
        "- /specs/schema/schema_v1.md\n"
        "- /specs/schema/review_snapshot_schema_v1.yaml\n"
        "- /specs/contract/12_runner_interface.md\n"
        "- /specs/contract/25_compatibility_matrix.md\n"
        "- /specs/contract/26_review_output_contract.md\n"
        "- /specs/governance/check_sets_v1.yaml\n"
        "Runner lane: rust|required | python|compatibility | php|compatibility | mixed\n\n"
        "## Scope Notes\n\n"
        "- What changed since last review:\n"
        "- What this run focused on:\n"
        "- Environment limitations:\n\n"
        "## Command Execution Log\n\n"
        "| command | status | exit_code | stdout_stderr_summary |\n"
        "|---|---|---:|---|\n"
        "| <command> | pass/fail/skipped | <code> | <summary> |\n\n"
        "## Findings\n\n"
        "| Severity | Verified/Hypothesis | File:Line | What | Why | When | Proposed fix |\n"
        "|---|---|---|---|---|---|---|\n"
        "| P1 | Verified | path:line | ... | ... | ... | ... |\n\n"
        "## Synthesis\n\n"
        "- North-star:\n"
        "- Top risks:\n"
        "- Definition of done:\n\n"
        "## Spec Candidates (YAML)\n\n"
        "```yaml\n"
        "- id: REVIEW-CANDIDATE-001\n"
        "  title: Replace with concise candidate title\n"
        "  type: contract.check\n"
        "  class: MUST\n"
        "  target_area: docs.reviews\n"
        "  acceptance_criteria:\n"
        "  - Define measurable acceptance condition\n"
        "  affected_paths:\n"
        "  - /specs/governance/cases/core/example.spec.md\n"
        "  risk: moderate\n"
        "```\n\n"
        "## Classification Labels\n\n"
        "- `REVIEW-CANDIDATE-001`: docs\n\n"
        "## Reject / Defer List\n\n"
        "- feature: <name>\n"
        "  why_defer: <reason>\n"
        "  revisit_trigger: <trigger>\n\n"
        "## Raw Output\n\n"
        "Paste the full AI output here. Keep content intact except light formatting cleanup.\n"
    )
    out_path.write_text(body, encoding="utf-8")
    print(out_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
