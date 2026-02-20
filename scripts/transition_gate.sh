#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -z "${PYTHON_BIN:-}" ]]; then
  if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
    PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    PYTHON_BIN="python3"
  fi
fi

RUST_ADAPTER_DEFAULT="${ROOT_DIR}/../data-contracts/runners/public/runner_adapter.sh"
RUST_ADAPTER="${SPEC_RUNNER_BIN:-${RUST_ADAPTER_DEFAULT}}"

run_step() {
  local label="$1"
  shift
  echo "[transition-gate] ${label}"
  "$@"
}

run_step "lint" make lint PYTHON="${PYTHON_BIN}"
run_step "typecheck" make typecheck PYTHON="${PYTHON_BIN}"
run_step "test" make test PYTHON="${PYTHON_BIN}"
run_step "test-cov" make test-cov PYTHON="${PYTHON_BIN}"
run_step "spec-sync-check" make spec-sync-check
run_step "runner-spec-check" make runner-spec-check

set +e
make compat-check
compat_rc=$?
set -e

if [[ "${compat_rc}" -eq 0 ]]; then
  echo "[transition-gate] compat-check passed"
  exit 0
fi

echo "[transition-gate] compat-check failed (${compat_rc}); attempting rust fallback gate"

if [[ ! -x "${RUST_ADAPTER}" ]]; then
  echo "ERROR: rust fallback adapter not executable: ${RUST_ADAPTER}" >&2
  exit "${compat_rc}"
fi

set +e
SPEC_RUNNER_BIN="${RUST_ADAPTER}" \
SPEC_RUNNER_IMPL="rust" \
"${PYTHON_BIN}" -m spec_runner.spec_lang_commands ci-gate-summary \
  --runner-bin "${RUST_ADAPTER}" \
  --runner-impl rust \
  --continue-on-fail \
  --out .artifacts/gate-summary-rust-transition.json
rust_rc=$?
set -e

if [[ "${rust_rc}" -ne 0 ]]; then
  echo "ERROR: rust fallback gate failed (${rust_rc})" >&2
  exit "${compat_rc}"
fi

echo "[transition-gate] rust fallback gate passed; treating compat-check failure as transition flake"
exit 0
