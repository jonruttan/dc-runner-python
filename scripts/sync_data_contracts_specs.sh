#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="${ROOT_DIR}/specs/upstream/data_contracts_lock_v1.yaml"
SNAP_ROOT="${ROOT_DIR}/specs/upstream/data-contracts"
MANIFEST_FILE="${ROOT_DIR}/specs/upstream/data-contracts.manifest.sha256"
DEFAULT_SOURCE="https://github.com/jonruttan/data-contracts.git"

INCLUDE_PATTERNS=(
  "specs/index.md"
  "specs/00_core/current.md"
  "specs/02_contracts/**"
  "specs/01_schema/**"
  "specs/03_conformance/**"
  "specs/04_governance/index.md"
  "specs/04_governance/check_*.yaml"
  "specs/04_governance/cases/core/**"
  "specs/04_governance/metrics/**"
)

EXCLUDE_PATTERNS=(
  "**/pending/**"
  "**/reviews/**"
  "**/snapshots/**"
)

usage() {
  cat <<USAGE
Usage:
  scripts/sync_data_contracts_specs.sh --check [--source <path-or-url>]
  scripts/sync_data_contracts_specs.sh --tag <tag-or-ref> [--source <path-or-url>] [--write]

Options:
  --check           Verify lock + manifest + snapshot consistency.
  --tag <value>     Upstream tag or ref to pin (required for write mode).
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

copy_selected_files() {
  local source_root="$1"
  local dest_root="$2"

  local tmp_files
  tmp_files="$(mktemp)"

  find "$source_root/specs" -type f | sed "s#^${source_root}/##" | LC_ALL=C sort > "$tmp_files"

  rm -rf "$dest_root"
  mkdir -p "$dest_root"

  local include_hits=()
  local i
  for ((i = 0; i < ${#INCLUDE_PATTERNS[@]}; i++)); do
    include_hits+=(0)
  done

  while IFS= read -r rel; do
    local include_match=0
    local idx
    for ((idx = 0; idx < ${#INCLUDE_PATTERNS[@]}; idx++)); do
      if [[ "$rel" == ${INCLUDE_PATTERNS[$idx]} ]]; then
        include_match=1
        include_hits[$idx]=1
      fi
    done
    [[ "$include_match" -eq 1 ]] || continue

    local exclude_match=0
    for ex in "${EXCLUDE_PATTERNS[@]}"; do
      if [[ "$rel" == $ex ]]; then
        exclude_match=1
        break
      fi
    done
    [[ "$exclude_match" -eq 0 ]] || continue

    mkdir -p "$dest_root/$(dirname "$rel")"
    cp "$source_root/$rel" "$dest_root/$rel"
  done < "$tmp_files"

  rm -f "$tmp_files"

  for ((i = 0; i < ${#INCLUDE_PATTERNS[@]}; i++)); do
    if [[ "${include_hits[$i]}" -ne 1 ]]; then
      echo "ERROR: include pattern matched no files: ${INCLUDE_PATTERNS[$i]}" >&2
      return 1
    fi
  done
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

verify_required_files_exist() {
  local snapshot_root="$1"
  local required=(
    "specs/index.md"
    "specs/00_core/current.md"
    "specs/02_contracts/index.md"
    "specs/02_contracts/policy_v1.yaml"
    "specs/02_contracts/traceability_v1.yaml"
    "specs/01_schema/index.md"
    "specs/01_schema/runner_certification_registry_v1.yaml"
    "specs/01_schema/runner_reference_v1.yaml"
    "specs/04_governance/index.md"
    "specs/04_governance/check_sets_v1.yaml"
    "specs/04_governance/check_prefix_map_v1.yaml"
    "specs/04_governance/cases/core/index.md"
  )

  local missing=0
  for rel in "${required[@]}"; do
    if [[ ! -f "$snapshot_root/$rel" ]]; then
      echo "ERROR: required snapshot file missing: $rel" >&2
      missing=1
    fi
  done

  [[ "$missing" -eq 0 ]]
}

verify_mode() {
  local source="$1"

  [[ -f "$LOCK_FILE" ]] || { echo "ERROR: lock file missing: $LOCK_FILE" >&2; return 1; }
  [[ -f "$MANIFEST_FILE" ]] || { echo "ERROR: manifest missing: $MANIFEST_FILE" >&2; return 1; }
  [[ -d "$SNAP_ROOT" ]] || { echo "ERROR: snapshot root missing: $SNAP_ROOT" >&2; return 1; }

  local lock_repo lock_tag lock_commit lock_file_count lock_manifest_hash lock_snapshot_root
  lock_repo="$(extract_lock_value "  repo" "$LOCK_FILE")"
  lock_tag="$(extract_lock_value "  tag" "$LOCK_FILE")"
  lock_commit="$(extract_lock_value "  commit" "$LOCK_FILE")"
  lock_snapshot_root="$(extract_lock_value "  root" "$LOCK_FILE")"
  lock_file_count="$(extract_lock_value "  file_count" "$LOCK_FILE")"
  lock_manifest_hash="$(extract_lock_value "  sha256_manifest" "$LOCK_FILE")"

  [[ -n "$lock_repo" ]] || { echo "ERROR: lock upstream.repo missing" >&2; return 1; }
  [[ -n "$lock_tag" ]] || { echo "ERROR: lock upstream.tag missing" >&2; return 1; }
  [[ "$lock_commit" =~ ^[0-9a-f]{40}$ ]] || { echo "ERROR: lock upstream.commit must be 40-char sha" >&2; return 1; }
  [[ "$lock_snapshot_root" == "specs/upstream/data-contracts" ]] || { echo "ERROR: lock snapshot.root unexpected: $lock_snapshot_root" >&2; return 1; }
  [[ "$lock_file_count" =~ ^[0-9]+$ ]] || { echo "ERROR: lock integrity.file_count must be integer" >&2; return 1; }
  [[ "$lock_manifest_hash" =~ ^[0-9a-f]{64}$ ]] || { echo "ERROR: lock integrity.sha256_manifest must be sha256" >&2; return 1; }

  local tmp_manifest
  tmp_manifest="$(mktemp)"
  write_manifest "$SNAP_ROOT" "$tmp_manifest"

  if ! diff -u "$MANIFEST_FILE" "$tmp_manifest" >/dev/null; then
    echo "ERROR: snapshot manifest drift detected. Run spec sync update." >&2
    rm -f "$tmp_manifest"
    return 1
  fi

  local computed_manifest_hash computed_file_count
  computed_manifest_hash="$(sha256_file "$MANIFEST_FILE")"
  computed_file_count="$(wc -l < "$MANIFEST_FILE" | tr -d ' ')"

  rm -f "$tmp_manifest"

  [[ "$computed_manifest_hash" == "$lock_manifest_hash" ]] || {
    echo "ERROR: lock manifest hash mismatch" >&2
    return 1
  }

  [[ "$computed_file_count" == "$lock_file_count" ]] || {
    echo "ERROR: lock file_count mismatch" >&2
    return 1
  }

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
    if resolved="$(resolve_ref_in_repo "$source_repo" "$lock_tag" 2>/dev/null)"; then
      local resolved_commit="${resolved%%;*}"
      if [[ "$resolved_commit" != "$lock_commit" ]]; then
        echo "ERROR: lock tag resolves to different commit in source" >&2
        [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"
        return 1
      fi
    else
      echo "WARN: lock tag '${lock_tag}' not found in source '${source}'; commit pinned locally only" >&2
    fi

    [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"
  fi

  echo "OK: upstream snapshot and lock are consistent"
}

write_mode() {
  local source="$1"
  local tag="$2"

  [[ -n "$tag" ]] || { echo "ERROR: --tag is required for write mode" >&2; return 2; }
  [[ -n "$source" ]] || source="$DEFAULT_SOURCE"

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
  if ! resolved="$(resolve_ref_in_repo "$source_repo" "$tag" 2>/dev/null)"; then
    echo "ERROR: cannot resolve tag/ref '${tag}' in source '${source}'" >&2
    [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"
    return 1
  fi

  local commit="${resolved%%;*}"
  local ref_kind="${resolved##*;}"

  if [[ "$ref_kind" != "tag" ]]; then
    echo "WARN: '${tag}' resolved as non-tag git ref; release workflow should use immutable tags." >&2
  fi

  local extract_dir
  extract_dir="$(mktemp -d)"
  create_snapshot_from_commit "$source_repo" "$commit" "$extract_dir"

  copy_selected_files "$extract_dir" "$SNAP_ROOT"
  write_manifest "$SNAP_ROOT" "$MANIFEST_FILE"

  local file_count manifest_hash now_utc
  file_count="$(wc -l < "$MANIFEST_FILE" | tr -d ' ')"
  manifest_hash="$(sha256_file "$MANIFEST_FILE")"
  now_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  mkdir -p "$(dirname "$LOCK_FILE")"
  cat > "$LOCK_FILE" <<LOCK
version: 1
upstream:
  repo: ${DEFAULT_SOURCE}
  tag: ${tag}
  commit: ${commit}
  synced_at_utc: "${now_utc}"
snapshot:
  root: specs/upstream/data-contracts
  include:
    - specs/index.md
    - specs/current.md
    - specs/contract/**
    - specs/01_schema/**
    - specs/conformance/**
    - specs/governance/index.md
    - specs/governance/check_*.yaml
    - specs/governance/cases/core/**
    - specs/governance/metrics/**
  exclude:
    - "**/pending/**"
    - "**/reviews/**"
    - "**/snapshots/**"
integrity:
  file_count: ${file_count}
  sha256_manifest: ${manifest_hash}
LOCK

  rm -rf "$extract_dir"
  [[ -n "$temp_repo" ]] && rm -rf "$temp_repo"

  verify_mode ""
  echo "OK: wrote lock + snapshot + manifest for ${tag} (${commit})"
}

MODE=""
TAG=""
SOURCE=""
WRITE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)
      MODE="check"
      shift
      ;;
    --tag)
      TAG="$2"
      MODE="write"
      WRITE=1
      shift 2
      ;;
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --write)
      WRITE=1
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

if [[ -z "$MODE" ]]; then
  usage >&2
  exit 2
fi

case "$MODE" in
  check)
    verify_mode "$SOURCE"
    ;;
  write)
    if [[ "$WRITE" -ne 1 ]]; then
      echo "ERROR: write mode requires --write or --tag" >&2
      exit 2
    fi
    write_mode "$SOURCE" "$TAG"
    ;;
  *)
    echo "ERROR: unsupported mode: $MODE" >&2
    exit 2
    ;;
esac
