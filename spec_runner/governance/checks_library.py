from __future__ import annotations

from spec_runner.governance.registry import checks_for_prefix


PREFIXES = ("library.", "normalization.", "naming.", "spec.", "tests.", "pending_status_markers")


def checks() -> dict[str, object]:
    return {k: v for k, v in checks_for_prefix(PREFIXES).items()}
