#!/usr/bin/env bash
set -euo pipefail

# Claude Code Skills Installer
# Usage: bash <(curl -s https://raw.githubusercontent.com/VetSecItPro/steelmotion-ops/main/install.sh)

REPO="https://github.com/VetSecItPro/steelmotion-ops.git"
TMPDIR=$(mktemp -d)
COMMANDS_DIR="$HOME/.claude/commands"
STANDARDS_DIR="$HOME/.claude/standards"

echo "Installing Claude Code Skills..."

# Clone repo
git clone --quiet --depth 1 "$REPO" "$TMPDIR/claude-code-skills"

# Create directories
mkdir -p "$COMMANDS_DIR" "$STANDARDS_DIR"

# Copy skills
SKILLS_COPIED=0
for file in "$TMPDIR/claude-code-skills/.claude/commands/"*.md; do
  [ -f "$file" ] || continue
  cp "$file" "$COMMANDS_DIR/"
  SKILLS_COPIED=$((SKILLS_COPIED + 1))
done

# Copy standards
STANDARDS_COPIED=0
for file in "$TMPDIR/claude-code-skills/.claude/standards/"*.md; do
  [ -f "$file" ] || continue
  cp "$file" "$STANDARDS_DIR/"
  STANDARDS_COPIED=$((STANDARDS_COPIED + 1))
done

# Cleanup
rm -rf "$TMPDIR"

echo ""
echo "Installed $SKILLS_COPIED skills to $COMMANDS_DIR"
echo "Installed $STANDARDS_COPIED standards to $STANDARDS_DIR"
echo ""
echo "Restart Claude Code to use your new skills."
echo ""
echo "Pipeline: /mdmp > /dev > /design > /smoketest > /sec-ship > /gh-ship"
echo "Full list: https://steelmotionllc.com/portfolio/software/claude-code-skills"
