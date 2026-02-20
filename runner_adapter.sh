#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

subcommand="${1:-}"
shift || true

case "$subcommand" in
  style-check)
    exec "${PYTHON_BIN}" -m spec_runner.spec_lang_commands spec-lang-lint "$@"
    ;;
  job-run)
    ref=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --ref)
          ref="${2:-}"
          shift 2
          ;;
        *)
          shift
          ;;
      esac
    done

    case "$ref" in
      "#GOVERNANCE_BASIC")
        exec "${PYTHON_BIN}" -m spec_runner.spec_lang_commands run-governance-specs --liveness-level basic
        ;;
      "#CONFORMANCE_PARITY")
        exec "${PYTHON_BIN}" -m spec_runner.spec_lang_commands compare-conformance-parity --python-only --cases specs/conformance/cases --out .artifacts/conformance-parity-python.json
        ;;
      *)
        echo "ERROR: unknown job ref: ${ref}" >&2
        exit 1
        ;;
    esac
    ;;
  governance)
    exec "${PYTHON_BIN}" -m spec_runner.spec_lang_commands run-governance-specs "$@"
    ;;
  conformance)
    exec "${PYTHON_BIN}" -m spec_runner.spec_lang_commands compare-conformance-parity "$@"
    ;;
  spec-runner)
    exec "${PYTHON_BIN}" -m spec_runner.spec_lang_commands "$@"
    ;;
  "")
    echo "ERROR: missing subcommand" >&2
    echo "Usage: ./runner_adapter.sh {style-check|job-run|governance|conformance|spec-runner} <args...>" >&2
    exit 2
    ;;
  *)
    echo "ERROR: unsupported subcommand: $subcommand" >&2
    echo "Usage: ./runner_adapter.sh {style-check|job-run|governance|conformance|spec-runner} <args...>" >&2
    exit 2
    ;;
esac
