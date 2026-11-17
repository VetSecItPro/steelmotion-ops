#!/usr/bin/env bash
# Run this repo's local CI (the command in .ci-local) and stamp the commit it passed on.
#
# WHY. CI minutes are billed; a PR opened on a commit that fails a check the laptop could have run pays
# for a whole CI cycle to learn it, then another to confirm the fix (one Next.js site repo averaged 2.5 cycles a
# PR in November 2026, about 48 minutes each). gh-push-guard.py refuses `gh pr create` in a repo that
# declares .ci-local until this script has passed on HEAD.
#
# The stamp is .reports/ci/local-ok/<full commit hash> (gitignored, never committed). It vouches for exactly
# the committed HEAD: the command always runs in a clean worktree of HEAD, and the stamp is written only when it exits 0.
# Usage: bash ~/.claude/ci-local.sh [repo]      exit status is the command's own
set -uo pipefail
repo="${1:-.}"
cd "$repo" || { echo "ci-local: no such directory: $repo"; exit 2; }
root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "ci-local: not a git repo"; exit 2; }
cd "$root" || exit 2
[ -f .ci-local ] || { echo "ci-local: this repo has no .ci-local; nothing to run (the guard does not require one)"; exit 0; }
head="$(git rev-parse HEAD)"
start=$(date +%s)
# Always a throwaway worktree of HEAD. Two ways a checkout lies about HEAD:
# - a dirty tree, often ANOTHER session's uncommitted edit (one Next.js site repo, 2026-11-05), or an untracked module CI never sees;
# - gitignored local files that CI never has (2026-11-11: a gitignored art folder named in the docs
#   passed the links test here and failed it on GitHub). Running in place on a clean tree hid the second one.
# Cost measured before the change: one Next.js site repo 347 s in a worktree against a 311 s median in place.
wt="$(mktemp -d "${TMPDIR:-/tmp}/ci-local.XXXXXX")"
trap 'git -C "$root" worktree remove --force "$wt" >/dev/null 2>&1 || true' EXIT  # also on Ctrl-C or a timeout
git worktree add -q --detach "$wt" "$head" || { echo "ci-local: could not create a clean worktree of HEAD"; exit 2; }
# Dependencies, not inputs: CI installs them, so the worktree gets them too.
# A real install, not a symlink: Turbopack refuses a node_modules that resolves outside the project root
# (one Next.js site repo, 2026-11-05: "Could not find the Next.js package"). pnpm hardlinks from its store, so it is quick.
if [ -f "$wt/pnpm-lock.yaml" ]; then (cd "$wt" && pnpm install --frozen-lockfile --prefer-offline --silent) || { echo "ci-local: install failed in the clean worktree"; exit 2; }
elif [ -f "$wt/package-lock.json" ]; then (cd "$wt" && npm ci --prefer-offline --no-audit --no-fund --silent) || { echo "ci-local: install failed in the clean worktree"; exit 2; }
elif [ -f "$wt/yarn.lock" ]; then (cd "$wt" && yarn install --frozen-lockfile --silent) || { echo "ci-local: install failed in the clean worktree"; exit 2; }
fi
# A Python virtualenv (tools/.venv) is a gitignored install CI rebuilds from its requirements; link it
# rather than rebuild it. Only a directory named .venv or venv holding pyvenv.cfg, so no other ignored file follows.
while IFS= read -r cfg; do
  rel="${cfg#./}"; rel="${rel%/pyvenv.cfg}"
  if [ ! -e "$wt/$rel" ] && git check-ignore -q "$rel"; then mkdir -p "$wt/$(dirname "$rel")"; ln -s "$root/$rel" "$wt/$rel"; fi
done < <(find . -maxdepth 4 \( -name node_modules -o -name .git \) -prune -o -path '*/.venv/pyvenv.cfg' -print -o -path '*/venv/pyvenv.cfg' -print 2>/dev/null)
echo "ci-local: running on a clean worktree of ${head:0:12} at $wt"
# The whole output is kept: a caller that shows only the last line otherwise loses why a run failed
# (2026-11-13: an exit 65 with no cause left anywhere, which did not reproduce).
mkdir -p "$root/.reports/ci"
(cd "$wt" && bash -e .ci-local) 2>&1 | tee "$root/.reports/ci/last-run.log"
rc=${PIPESTATUS[0]}
git worktree remove --force "$wt" >/dev/null 2>&1 || true
secs=$(( $(date +%s) - start ))
mkdir -p .reports/ci/local-ok
ts="$(TZ=America/Chicago date '+%Y-%m-%dT%H:%M:%S%z')"
if [ "$rc" -eq 0 ]; then
  : >| ".reports/ci/local-ok/$head"
  echo "ci-local: PASSED in ${secs}s; stamped ${head:0:12}"
else
  echo "ci-local: FAILED (exit $rc) after ${secs}s; no stamp; full log: $root/.reports/ci/last-run.log"
fi
logdir="${ACTIONS_GUARD_LOG_DIR:-$HOME/.claude/logs}"; mkdir -p "$logdir"
printf '{"ts":"%s","event":"ci_local","repo":"%s","commit":"%s","exit":%d,"seconds":%d}\n' \
  "$ts" "$root" "$head" "$rc" "$secs" | tee -a .reports/ci/ledger.jsonl >> "$logdir/actions-ledger.jsonl"
exit "$rc"
