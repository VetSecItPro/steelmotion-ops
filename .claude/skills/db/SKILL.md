---
name: db
description: "Database schema, migrations, drift detection and data management, safely. Detects the provider and ORM, introspects the real schema, catches drift between code and database, generates reversible migrations, and never applies to production without explicit confirmation. Data loss is the thing it exists to prevent."
when_to_use: 'Trigger phrases: "DB migration", "schema change", "RLS policy", "database drift", "add a column", "migrate the database", "generate migration", "row level security". Run for any schema change, and whenever code and database may have drifted apart.'
---

# /db - schema, migrations, drift, data management

**Spine. Survives compaction. The safety rules below must never be the part that gets dropped** -
they are what stands between a schema change and lost data.

| File | Read at | Holds |
|---|---|---|
| `stacks.md` | Phase 1 | provider + ORM detection, per-stack migration commands |
| `phases.md` | throughout | introspection, drift, migration generation, apply, validate |
| `reference.md` | report | report format, RLS patterns, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)

## Safety rules - non-negotiable

1. **Never lose data.** A migration that could drop a column, table or row states the risk in
   capitals and requires explicit confirmation. Prefer an additive path (new column + backfill +
   later cleanup) over a destructive one, always.
2. **Every migration is reversible.** A `down` that actually restores the prior state, or an explicit
   "irreversible - here is why and here is the backup step" where it genuinely cannot be.
3. **Local before production, no exceptions.** A migration is proven against a local or branch
   database before it is even recommended for production.
4. **Production apply requires human confirmation.** The skill pauses and asks before any change to a
   production database. It never auto-applies to prod, regardless of how safe the change looks.
5. **Prefer a code fix over a schema change.** When code and schema have drifted, fixing the query is
   usually right and reversible; altering the schema to match a bug is not. Change the schema only
   when the schema is what is wrong.
6. **Types stay in sync.** Regenerate ORM/TypeScript types after every schema change, in the same
   step, so the type layer never lies about the database.
7. **Back up before a destructive or production change.** Confirm a restorable backup exists before
   anything that cannot be trivially undone.

## Critical: read before assuming

**Detect the provider and ORM. Never assume Supabase, Postgres, or Prisma.** A repo may use Postgres
+ Drizzle, MySQL + Prisma, SQLite + Kysely, MongoDB + Mongoose, or raw SQL. The safe procedure differs
per stack (`stacks.md`). Detecting wrong means generating a migration in the wrong dialect.

## Modes

```
/db                   detect, introspect, check drift, propose the safe change
/db --audit           introspect and report only; change nothing
/db --drift           drift detection between code/schema and the live database only
/db --migrate <desc>  generate a reversible migration for the described change
/db --rls             review or generate row-level-security policies
/db --types           regenerate types from the current schema
/db --apply           apply pending migrations LOCALLY (prod still needs confirmation)
```

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 1 | Detect | provider, ORM, connection method, environments (local/branch/prod) |
| 2 | Introspect | the real current schema, from the database, not from the migration files |
| 3 | Drift | where code/migrations and the live schema disagree |
| 4 | Analyse | is the fix a code change or a schema change? (rule 5) |
| 5 | Generate | a reversible migration with a WHY comment, if a schema change is right |
| 6 | Prove locally | run up, verify, run down, verify - both directions |
| 7 | Validate | data integrity and constraints intact after the change |
| 8 | Types | regenerate; confirm the type layer matches |
| 9 | Report | with the rollback path and, for prod, the confirmation gate |

Phases 5-9 are the half a long run loses to compaction if not held here. **Phase 6 - proving the
down migration actually restores state - is the one that makes "reversible" true rather than
claimed.**

## Row-level security

Where the stack supports RLS (Postgres, Supabase), a table holding per-user or per-tenant data
without an RLS policy is a finding, not a preference. Every policy is tested from the perspective of
each role: the owner can, another user cannot, anonymous cannot. `FORCE ROW LEVEL SECURITY` where the
table owner would otherwise bypass it. Detail and patterns in `reference.md`.

## Human decision triggers

Stop and ask, never decide alone: any production apply; any change that could lose data; dropping a
column or table; a type change that could truncate; an RLS change that could widen access; a
migration with no safe rollback.

## Definition of done

- Provider and ORM detected correctly; migration in the right dialect
- Drift resolved at the right layer (code fix preferred where the schema is correct)
- Migration reversible and proven both directions locally
- Data integrity validated after
- Types regenerated and in sync
- Production changes gated behind explicit confirmation, never auto-applied
- Report written with the rollback path; SITREP ends with "Suggested next"
