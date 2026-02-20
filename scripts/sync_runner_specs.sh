#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="${ROOT_DIR}/specs/upstream/resolved_contract_set_lock_v1.yaml"
LOCK_HASH_FILE="${ROOT_DIR}/specs/upstream/resolved_contract_set_lock_v1.sha256"
SNAP_ROOT="${ROOT_DIR}/specs/upstream/dc-runner-spec"
MANIFEST_FILE="${ROOT_DIR}/specs/upstream/dc-runner-spec.manifest.sha256"
DEFAULT_SOURCE="https://github.com/jonruttan/dc-runner-spec.git"
RUNNER="python"
ROOT_CONTRACT_SET="python_runner_contract_set"
LOCK_FILENAME="resolved_contract_set_lock_v1.yaml"
RESOLVER_BIN_DEFAULT="${ROOT_DIR}/../data-contracts/scripts/contract-set"
RESOLVER_BIN="${CONTRACT_SET_RESOLVER_BIN:-${RESOLVER_BIN_DEFAULT}}"

usage() {
  cat <<USAGE
Usage:
  scripts/sync_runner_specs.sh --check [--source <path-or-url>]
  scripts/sync_runner_specs.sh --tag <tag-or-ref> [--source <path-or-url>] [--write]

Options:
  --check           Verify resolved lock + lock hash + snapshot integrity.
  --tag <value>     Upstream tag or ref to pin (required for write mode; use WORKTREE for local uncommitted source).
  --source <value>  Upstream git source (optional for --check; default for --tag is ${DEFAULT_SOURCE}).
  --write           Perform sync write (default when --tag is provided).
USAGE
}

sha256_file() {
  local file="$1"
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$file" | awk '{print $1}'
  else
    sha256sum "$file" | awk '{print $1}'
  fi
}

is_local_git_repo() {
  local source="$1"
  [[ -d "$source/.git" ]]
}

resolve_ref_in_repo() {
  local repo="$1"
  local ref="$2"
  local commit=""
  local kind="tag"

  if commit="$(git -C "$repo" rev-parse --verify "refs/tags/${ref}^{commit}" 2>/dev/null)"; then
    :
  elif commit="$(git -C "$repo" rev-parse --verify "${ref}^{commit}" 2>/dev/null)"; then
    kind="ref"
  else
    return 1
  fi

  printf '%s;%s\n' "$commit" "$kind"
}

create_snapshot_from_commit() {
  local repo="$1"
  local commit="$2"
  local out_dir="$3"

  mkdir -p "$out_dir"
  git -C "$repo" archive "$commit" | tar -x -C "$out_dir"
}

write_manifest() {
  local snapshot_root="$1"
  local manifest_file="$2"

  mkdir -p "$(dirname "$manifest_file")"
  : > "$manifest_file"

  while IFS= read -r rel; do
    local hash
    hash="$(sha256_file "$snapshot_root/$rel")"
    printf '%s  %s\n' "$hash" "$rel" >> "$manifest_file"
  done < <(cd "$snapshot_root" && find . -type f | sed 's#^\./##' | LC_ALL=C sort)
}

extract_lock_value() {
  local key="$1"
  local file="$2"
  awk -F': ' -v key="$key" '$1 == key {print $2}' "$file" | sed 's/^"//; s/"$//'
}

copy_resolved_tree() {
  local resolved_root="$1"
  local dest_root="$2"

  rm -rf "$dest_root"
  mkdir -p "$dest_root"

  while IFS= read -r rel; do
    [[ "$rel" == "$LOCK_FILENAME" ]] && continue
    mkdir -p "$dest_root/$(dirname "$rel")"
    cp "$resolved_root/$rel" "$dest_root/$rel"
  done < <(cd "$resolved_root" && find . -type f | sed 's#^\./##' | LC_ALL=C sort)
}

verify_required_files_exist() {
  local snapshot_root="$1"
  local required=(
    "specs/index.md"
    "specs/impl/shared/makefile_help_output_v1.md"
    "specs/impl/python/index.md"
    "specs/impl/python/runner_build_tool_contract_v1.yaml"
    "specs/impl/python/runner_spec_registry_v1.yaml"
    "specs/impl/python/cases/index.md"
  )

  local missing=0
  for rel in "${required[@]}"; do
    if [[ ! -f "$snapshot_root/$rel" ]]; then
      echo "ERROR: required runner-spec file missing: $rel" >&2
      missing=1
    fi
  done

  [[ "$missing" -eq 0 ]]
}

verify_mode() {
  local source="$1"

  [[ -f "$LOCK_FILE" ]] || { echo "ERROR: lock file missing: $LOCK_FILE" >&2; return 1; }
  [[ -f "$LOCK_HASH_FILE" ]] || { echo "ERROR: lock hash file missing: $LOCK_HASH_FILE" >&2; return 1; }
  [[ -f "$MANIFEST_FILE" ]] || { echo "ERROR: manifest missing: $MANIFEST_FILE" >&2; return 1; }
  [[ -d "$SNAP_ROOT" ]] || { echo "ERROR: snapshot root missing: $SNAP_ROOT" >&2; return 1; }

  local lock_root lock_runner lock_commit lock_ref lock_repo lock_file_count lock_manifest_hash
  lock_root="$(extract_lock_value "root_contract_set" "$LOCK_FILE")"
  lock_runner="$(extract_lock_value "runner" "$LOCK_FILE")"
  lock_repo="$(extract_lock_value "  repo" "$LOCK_FILE")"
  lock_ref="$(extract_lock_value "  ref" "$LOCK_FILE")"
  lock_commit="$(extract_lock_value "  commit" "$LOCK_FILE")"
  lock_file_count="$(extract_lock_value "  file_count" "$LOCK_FILE")"
  lock_manifest_hash="$(extract_lock_value "  sha256_manifest" "$LOCK_FILE")"

  [[ "$lock_root" == "$ROOT_CONTRACT_SET" ]] || { echo "ERROR: lock root_contract_set mismatch: $lock_root" >&2; return 1; }
  [[ "$lock_runner" == "$RUNNER" ]] || { echo "ERROR: lock runner mismatch: $lock_runner" >&2; return 1; }
  [[ -n "$lock_repo" ]] || { echo "ERROR: lock source.repo missing" >&2; return 1; }
  [[ -n "$lock_ref" ]] || { echo "ERROR: lock source.ref missing" >&2; return 1; }
  [[ "$lock_commit" =~ ^[0-9a-f]{40}$ || "$lock_commit" == "unknown" ]] || {
    echo "ERROR: lock source.commit must be 40-char sha or unknown" >&2
    return 1
  }
  [[ "$lock_file_count" =~ ^[0-9]+$ ]] || { echo "ERROR: lock integrity.file_count must be integer" >&2; return 1; }
  [[ "$lock_manifest_hash" =~ ^[0-9a-f]{64}$ ]] || { echo "ERROR: lock integrity.sha256_manifest must be sha256" >&2; return 1; }

  local computed_lock_hash expected_lock_hash
  computed_lock_hash="$(sha256_file "$LOCK_FILE")"
  expected_lock_hash="$(awk '{print $1}' "$LOCK_HASH_FILE")"
  [[ "$computed_lock_hash" == "$expected_lock_hash" ]] || {
    echo "ERROR: resolved lock hash mismatch" >&2
    return 1
  }

  local tmp_manifest
  tmp_manifest="$(mktemp)"
  write_manifest "$SNAP_ROOT" "$tmp_manifest"

  if ! diff -u "$MANIFEST_FILE" "$tmp_manifest" >/dev/null; then
    echo "ERROR: runner-spec manifest drift detected. Run runner-spec sync update." >&2
    rm -f "$tmp_manifest"
    return 1
  fi

  rm -f "$tmp_manifest"
  verify_required_files_exist "$SNAP_ROOT"

  if [[ -n "$source" ]]; then
    local source_repo=""
    local temp_repo=""
    if is_local_git_repo "$source"; then
      source_repo="$source"
    else
      temp_repo="$(mktemp -d)"
      git clone --quiet --filter=blob:none --no-checkout "$source" "$temp_repo/source"
      source_repo="$temp_repo/source"
    fi

    local resolved
    if [[ "$lock_ref" == "WORKTREE" ]]; then
      :
    elif resolved="$(resolve_ref_in_repo "$source_repo" "$lock_ref" 2>/dev/null)"; then
      local resolved_commit="${resolved%%;*}"
      if [[ "$lock_commit" != "unknown" && "$resolved_commit" != "$lock_commit" ]]; then
        echo "ERROR: lock ref resolves to different commit in source" >&2
        [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"
        return 1
      fi
    else
      echo "WARN: lock ref '${lock_ref}' not found in source '${source}'; commit pinned locally only" >&2
    fi

    [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"
  fi

  echo "OK: resolved runner-spec snapshot and lock are consistent"
}

write_mode() {
  local source="$1"
  local tag="$2"

  [[ -n "$tag" ]] || { echo "ERROR: --tag is required for write mode" >&2; return 2; }
  [[ -n "$source" ]] || source="$DEFAULT_SOURCE"
  [[ -x "$RESOLVER_BIN" ]] || { echo "ERROR: resolver not executable: $RESOLVER_BIN" >&2; return 1; }

  local source_repo=""
  local temp_repo=""
  if is_local_git_repo "$source"; then
    source_repo="$source"
  else
    temp_repo="$(mktemp -d)"
    git clone --quiet --filter=blob:none --no-checkout "$source" "$temp_repo/source"
    source_repo="$temp_repo/source"
  fi

  local commit=""
  local ref_kind=""
  local extract_dir
  extract_dir="$(mktemp -d)"
  if [[ "$tag" == "WORKTREE" && -d "$source_repo/.git" ]]; then
    commit="$(git -C "$source_repo" rev-parse HEAD 2>/dev/null || true)"
    [[ -n "$commit" ]] || commit="unknown"
    ref_kind="worktree"
    (cd "$source_repo" && tar --exclude='.git' -cf - .) | tar -xf - -C "$extract_dir"
  else
    local resolved
    if ! resolved="$(resolve_ref_in_repo "$source_repo" "$tag" 2>/dev/null)"; then
      echo "ERROR: cannot resolve tag/ref '${tag}' in source '${source}'" >&2
      [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"
      rm -rf "$extract_dir"
      return 1
    fi
    commit="${resolved%%;*}"
    ref_kind="${resolved##*;}"
    create_snapshot_from_commit "$source_repo" "$commit" "$extract_dir"
  fi

  if [[ "$ref_kind" != "tag" && "$ref_kind" != "worktree" ]]; then
    echo "WARN: '${tag}' resolved as non-tag git ref; release workflow should use immutable tags." >&2
  fi

  local resolved_dir
  resolved_dir="$(mktemp -d)"
  "$RESOLVER_BIN" resolve \
    --runner "$RUNNER" \
    --root "$ROOT_CONTRACT_SET" \
    --out "$resolved_dir" \
    --repo-root "$extract_dir" \
    --source-repo "$source" \
    --source-ref "$tag" \
    --source-commit "$commit"

  [[ -f "$resolved_dir/$LOCK_FILENAME" ]] || {
    echo "ERROR: resolver did not emit ${LOCK_FILENAME}" >&2
    rm -rf "$extract_dir" "$resolved_dir"
    [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"
    return 1
  }

  copy_resolved_tree "$resolved_dir" "$SNAP_ROOT"
  cp "$resolved_dir/$LOCK_FILENAME" "$LOCK_FILE"
  printf '%s  %s\n' "$(sha256_file "$LOCK_FILE")" "${LOCK_FILENAME}" > "$LOCK_HASH_FILE"
  write_manifest "$SNAP_ROOT" "$MANIFEST_FILE"

  rm -rf "$extract_dir" "$resolved_dir"
  [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"

  echo "OK: synced runner-spec resolved contract set from ${source} @ ${tag} (${commit})"
}

MODE=""
TAG=""
SOURCE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)
      MODE="check"
      shift
      ;;
    --tag)
      TAG="$2"
      shift 2
      ;;
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --write)
      MODE="write"
      shift
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

if [[ -n "$TAG" && -z "$MODE" ]]; then
  MODE="write"
fi

if [[ "$MODE" == "check" ]]; then
  verify_mode "$SOURCE"
elif [[ "$MODE" == "write" ]]; then
  write_mode "$SOURCE" "$TAG"
else
  echo "ERROR: choose --check or --tag <value>" >&2
  usage >&2
  exit 2
fi
