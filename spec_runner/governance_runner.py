from __future__ import annotations

from spec_runner.governance_runtime import main as _governance_main


def run_governance_specs_main(argv: list[str] | None = None) -> int:
    return int(_governance_main(argv))
