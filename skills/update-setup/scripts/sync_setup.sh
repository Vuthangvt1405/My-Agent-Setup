#!/usr/bin/env bash
# Sync this project's Claude setup with the My-Agent-Setup GitHub repo.
# Usage: sync_setup.sh status|pull|push "<commit message>"
set -euo pipefail

REPO_URL="https://github.com/Vuthangvt1405/My-Agent-Setup.git"
BRANCH="main"
CLONE_DIR="${MY_AGENT_SETUP_DIR:-$HOME/.cache/my-agent-setup}"
PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# project path -> path in My-Agent-Setup
MAPPINGS=(
  "CLAUDE.md:CLAUDE.md"
  ".claude/settings.json:settings.json"
  ".claude/skills/:skills/"
)

prepare_clone() {
  if [ ! -d "$CLONE_DIR/.git" ]; then
    git clone -q "$REPO_URL" "$CLONE_DIR"
  fi
  if [ -n "$(git -C "$CLONE_DIR" status --porcelain)" ]; then
    echo "ERROR: $CLONE_DIR has uncommitted changes; resolve them first." >&2
    exit 1
  fi
  git -C "$CLONE_DIR" fetch -q origin "$BRANCH"
  git -C "$CLONE_DIR" checkout -q "$BRANCH"
  git -C "$CLONE_DIR" reset -q --hard "origin/$BRANCH"
}

copy_entries() { # $1 = direction: to-remote | to-project
  for mapping in "${MAPPINGS[@]}"; do
    local project_path="$PROJECT_ROOT/${mapping%%:*}" remote_path="$CLONE_DIR/${mapping##*:}"
    local source="$project_path" target="$remote_path"
    [ "$1" = to-project ] && source="$remote_path" target="$project_path"
    [ -e "$source" ] || continue
    if [ -d "$source" ]; then
      mkdir -p "$target"
      rsync -a --delete "$source" "$target"
    else
      mkdir -p "$(dirname "$target")"
      cp "$source" "$target"
    fi
  done
}

show_differences() {
  for mapping in "${MAPPINGS[@]}"; do
    diff -rq "$PROJECT_ROOT/${mapping%%:*}" "$CLONE_DIR/${mapping##*:}" 2>&1 \
      | sed -e "s#$PROJECT_ROOT/#project:#g" -e "s#$CLONE_DIR/#remote:#g" || true
  done
}

case "${1:-status}" in
  status)
    prepare_clone
    echo "remote: $REPO_URL @ $(git -C "$CLONE_DIR" log -1 --format='%h %s')"
    differences="$(show_differences)"
    if [ -z "$differences" ]; then echo "IN SYNC"; else echo "DIFFERENCES:"; echo "$differences"; fi
    ;;
  pull)
    prepare_clone
    show_differences
    copy_entries to-project
    echo "PULLED $(git -C "$CLONE_DIR" log -1 --format='%h %s')"
    ;;
  push)
    message="${2:?commit message required}"
    prepare_clone
    copy_entries to-remote
    git -C "$CLONE_DIR" add -A -- CLAUDE.md settings.json skills
    if git -C "$CLONE_DIR" diff --cached --quiet; then echo "NOTHING TO PUSH"; exit 0; fi
    git -C "$CLONE_DIR" diff --cached --stat
    git -C "$CLONE_DIR" commit -q -m "$message"
    git -C "$CLONE_DIR" push -q origin "$BRANCH"
    echo "PUSHED $(git -C "$CLONE_DIR" log -1 --format='%h %s')"
    ;;
  *) echo "usage: $0 status|pull|push \"<message>\"" >&2; exit 2 ;;
esac
