#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYNC_SCRIPT="${ROOT_DIR}/scripts/sync_runner_specs.sh"
SOURCE=""

usage() {
  cat <<USAGE
Usage:
  scripts/verify_runner_specs.sh [--source <path-or-url>]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ -x "$SYNC_SCRIPT" ]] || { echo "ERROR: sync script not executable: $SYNC_SCRIPT" >&2; exit 1; }

if [[ -n "$SOURCE" ]]; then
  "$SYNC_SCRIPT" --check --source "$SOURCE"
else
  "$SYNC_SCRIPT" --check
fi

if [[ -f "$ROOT_DIR/specs/upstream/dc_runner_spec_lock_v1.yaml" ]]; then
  echo "ERROR: noncanonical lock file detected (specs/upstream/dc_runner_spec_lock_v1.yaml); migrate to resolved_contract_set_lock_v1.yaml" >&2
  exit 1
fi

echo "OK: runner-specific spec ingestion is consistent"
