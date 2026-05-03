# Multi-Repo Awareness

**Reference standard for skills that operate on git repos.** When run in a workspace with multiple sibling repos, surface their state without cross-traversing.

## When to apply

Apply to any skill that operates on a git repo: `/gh-ship`, `/sec-ship`, `/test-ship`, `/qatest`, `/ship`, `/monitor`, `/cleancode`, `/deps`, `/perf`.

## The pattern

### Detect workspace structure

```bash
WORKSPACE_PARENT=$(git rev-parse --show-toplevel | xargs dirname)
SIBLING_STATES=()
for sibling in "$WORKSPACE_PARENT"/*/; do
  if [ -d "$sibling/.git" ] && [ "$(realpath $sibling)" != "$(git rev-parse --show-toplevel)" ]; then
    pushd "$sibling" >/dev/null
    name=$(basename "$sibling")
    branch=$(git branch --show-current)
    uncommitted=$(git status --porcelain | wc -l | tr -d ' ')
    unpushed=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
    SIBLING_STATES+=("$name|$branch|uncommitted=$uncommitted|unpushed=$unpushed")
    popd >/dev/null
  fi
done
```

### Use the data

The skill MUST:
- Operate ONLY on cwd's repo (never auto-traverse)
- Surface SIBLING_STATES in the SITREP at end of run
- Suggest "run /<skill> from inside <sibling>/" if siblings have pending state

The skill MUST NOT:
- Run destructive operations on sibling repos
- Stage changes across multiple repos
- Assume sibling state without checking

## Why this matters

Real-world workspaces have multiple repos. Examples:
- `~/vibecode-projects/nolan-openclaw/` contains `mission-control`, `nolan-infra`, etc.
- A monorepo with sub-projects each in their own git submodule

If the skill operates on cwd silently, the operator forgets the others. Then they discover days later that "I shipped one repo but the sibling has uncommitted changes." Surfacing prevents this class of bug.

## SITREP integration

```
🌐 Sibling repos in workspace
   mission-control: branch=main, uncommitted=0, unpushed=0  ✅
   nolan-infra:     branch=main, uncommitted=2, unpushed=1  ⚠️
                    [run /gh-ship from inside if changes pending]
```

## Application checklist

For any repo-operating skill being audited:

- [ ] Add "multi-repo scan" stage early in the pipeline
- [ ] Include SIBLING_STATES output in the final SITREP
- [ ] Document explicit non-traversal in CRITICAL RULES
- [ ] Note in DESIGN DECISIONS: WHY scan-and-report vs cross-traverse
