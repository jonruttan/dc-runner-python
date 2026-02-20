from spec_runner import governance_runtime
from spec_runner.governance.cache import reset_scan_caches


def test_reset_scan_caches_clears_runner_cache() -> None:
    governance_runtime._RUNNER_CERTIFY_CACHE[(1, "root", "rust")] = (0, "ok")
    assert governance_runtime._RUNNER_CERTIFY_CACHE
    reset_scan_caches()
    assert governance_runtime._RUNNER_CERTIFY_CACHE == {}
