from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_makefile_has_required_help_renderer_shape() -> None:
    raw = MAKEFILE.read_text(encoding="utf-8")

    assert "help: ## Display this help section" in raw
    assert "@awk 'BEGIN {FS = \":.*?## \"}" in raw
    for group in ("##@ Core", "##@ Specs", "##@ Transition", "##@ Aggregate"):
        assert group in raw


def test_make_help_renders_required_groups_and_targets() -> None:
    cp = subprocess.run(
        ["make", "help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    out = _strip_ansi(cp.stdout)

    for group in ("Core", "Specs", "Transition", "Aggregate"):
        assert group in out

    for target in (
        "help",
        "setup",
        "test",
        "test-cov",
        "lint",
        "typecheck",
        "smoke",
        "spec-sync",
        "spec-sync-check",
        "compat-check",
        "runner-spec-sync",
        "runner-spec-check",
        "transition-gate",
        "verify",
    ):
        assert re.search(rf"(^|\n)\s*{re.escape(target)}\s+", out), f"missing target {target}"
