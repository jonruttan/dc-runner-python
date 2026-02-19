#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

subcommand="${1:-<subcommand>}"
echo "ERROR: python runner adapter is retired from runtime gate execution (DCRUN-IMPL-002)." >&2
echo "Use rust impl instead: ./runners/public/runner_adapter.sh --impl rust ${subcommand}" >&2
exit 2
