#!/usr/bin/env bash
# Fail if SKILL_ROUTER.md no longer matches the skills actually on disk.
#
# WHY A SCRIPT AND NOT A RULE. ~/.claude/CLAUDE.md already says "run the generator after
# adding, renaming or deleting any skill". That is a rule enforced by memory, and the
# measured result of the previous hand-maintained router was: 31 skills named against an
# estate of 40, 6 routed that did not exist, and 15 live skills it had never heard of,
# repo-bootstrap among them. Nothing failed while that was true, which is why it lasted.
#
# WHY IT IGNORES THE TIMESTAMP. The generator stamps "generated from the filesystem
# <date time>" on every run, so a naive diff reports drift every single time. A guard that
# is always red gets switched off within a week, and then it protects nothing. Only the
# CONTENT is compared.
#
#   check-skill-router.sh          report; exit 1 on drift
#   check-skill-router.sh --fix    regenerate, then report
set -u
cd "$(dirname "$0")" || exit 1
gen="python3 $PWD/generate-skill-router.py"
router="standards/SKILL_ROUTER.md"

strip() { grep -v "generated from the filesystem" "$1"; }

if [ "${1:-}" = "--fix" ]; then
  $gen >/dev/null 2>&1 && echo "REGENERATED  $router"
fi

before=$(mktemp); after=$(mktemp)
trap 'rm -f "$before" "$after"' EXIT
strip "$router" > "$before"
cp "$router" "$router.guardtmp"
$gen >/dev/null 2>&1
strip "$router" > "$after"
command mv -f "$router.guardtmp" "$router"   # leave the committed file exactly as found

# the estate, counted from the filesystem rather than trusted from the document
# A directory under skills/ is only a SKILL if it contains a SKILL.md. Corrected
# 2026-09-29: `skills/synced/` is Claude Code's own synced-skills cache, holding
# UUID-named subdirectories and `.bucket-*` marker files and no SKILL.md at all, so
# the old `ls -d skills/*/` counted it and this guard reported `43 on disk, 42 named`
# in every session for days. The ROUTER was right the whole time. Worse, the obvious
# response to the red line is to run the generator, which would have written the
# cache directory in AS a skill.
on_disk=$( { ls commands/*.md 2>/dev/null | sed 's|.*/||;s|\.md$||'; \
             for d in skills/*/; do [ -f "$d/SKILL.md" ] && basename "$d"; done; \
           } | sort -u | wc -l | tr -d ' ')
listed=$(grep -oE '^\| `/[a-z0-9:-]+`' "$router" | tr -d '|` ' | sed 's#^/##' | sort -u | wc -l | tr -d ' ')

if [ "$on_disk" = "0" ]; then
  echo "FAIL  counted 0 skills on disk. Refusing to report - the measurement is broken, not the estate."
  exit 1
fi

rc=0
if cmp -s "$before" "$after"; then
  echo "OK    router content matches the skills on disk"
else
  echo "FAIL  SKILL_ROUTER.md is STALE. A skill was added, renamed or removed without regenerating."
  echo "      Fix:  $0 --fix    then commit"
  rc=1
fi

if [ "$on_disk" != "$listed" ]; then
  echo "FAIL  $on_disk skills on disk, $listed named in the router."
  rc=1
else
  echo "OK    $listed skills on disk, all named in the router"
fi
exit $rc
