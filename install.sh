#!/usr/bin/env bash
set -euo pipefail

# Claude Code skills installer.
# Usage: bash <(curl -s https://raw.githubusercontent.com/VetSecItPro/steelmotion-ops/main/install.sh)
#
# Copies skills to ~/.claude/skills/, commands to ~/.claude/commands/, standards to ~/.claude/standards/,
# and the helper scripts, backlog template and two agents to ~/.claude/. Anything it would replace is copied first to
# ~/.claude/.steelmotion-ops-backup-<timestamp>/, so a local change is never lost.

REPO="${STEELMOTION_OPS_REPO:-https://github.com/VetSecItPro/steelmotion-ops.git}"
CLAUDE_DIR="$HOME/.claude"
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$CLAUDE_DIR/.steelmotion-ops-backup-$STAMP"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "Installing Claude Code skills..."
git clone --quiet --depth 1 "$REPO" "$WORK/repo"
SRC="$WORK/repo/.claude"
mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/commands" "$CLAUDE_DIR/standards" "$CLAUDE_DIR/templates" "$CLAUDE_DIR/agents"

BACKED_UP=0
backup() {  # $1: a path under ~/.claude about to be replaced
  [ -e "$1" ] || return 0
  local rel="${1#"$CLAUDE_DIR"/}"
  mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
  cp -R "$1" "$BACKUP_DIR/$rel"
  BACKED_UP=$((BACKED_UP + 1))
}

SKILLS=0
for dir in "$SRC/skills/"*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  backup "$CLAUDE_DIR/skills/$name"
  rm -rf "${CLAUDE_DIR:?}/skills/$name"
  cp -R "$dir" "$CLAUDE_DIR/skills/$name"
  SKILLS=$((SKILLS + 1))
done

COMMANDS=0
for file in "$SRC/commands/"*.md; do
  [ -f "$file" ] || continue
  backup "$CLAUDE_DIR/commands/$(basename "$file")"
  cp "$file" "$CLAUDE_DIR/commands/"
  COMMANDS=$((COMMANDS + 1))
done

STANDARDS=0
for file in "$SRC/standards/"*.md; do
  [ -f "$file" ] || continue
  backup "$CLAUDE_DIR/standards/$(basename "$file")"
  cp "$file" "$CLAUDE_DIR/standards/"
  STANDARDS=$((STANDARDS + 1))
done

TOOLS=0
for rel in ci-local.sh generate-skill-router.py check-skill-router.sh templates/backlog.md agents/readonly-verifier.md agents/scoped-implementer.md; do
  [ -f "$SRC/$rel" ] || continue
  backup "$CLAUDE_DIR/$rel"
  cp "$SRC/$rel" "$CLAUDE_DIR/$rel"
  TOOLS=$((TOOLS + 1))
done
chmod +x "$CLAUDE_DIR/ci-local.sh" "$CLAUDE_DIR/check-skill-router.sh" 2>/dev/null || true

echo ""
echo "Installed $SKILLS skills, $COMMANDS commands, $STANDARDS standards and $TOOLS helper files into $CLAUDE_DIR"
if [ "$BACKED_UP" -gt 0 ]; then
  echo "Replaced $BACKED_UP existing items; the old copies are in $BACKUP_DIR"
fi
echo ""
echo "Restart Claude Code to load them."
echo "Full list: https://steelmotionllc.com/portfolio/software/claude-code-skills"
