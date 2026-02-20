from __future__ import annotations


def reset_scan_caches() -> None:
    from spec_runner import governance_runtime as legacy

    legacy._reset_scan_caches()
