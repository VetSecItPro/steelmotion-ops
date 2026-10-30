# /db - report, RLS patterns, SITREP

## Report

`.db-reports/DB-<YYYYMMDD-HHMM>.md`, written progressively.

```markdown
# Database Report: <project>
**Provider / ORM:** <detected>  |  **Target env:** <local | branch | prod>
**Mode:** <audit | drift | migrate | rls | types | apply>

## Drift
| Object | Live | Code expects | Resolution |
|---|---|---|---|
| users.deleted_at | absent | column | code fix - remove the reference (was a bug) |

## Migration
**<name>** - <what and why>
- Reversible: yes | irreversible (<reason> + backup step)
- Data risk: none | <describes the risk>
- Proved locally: up OK, down restored prior state OK

## RLS
| Table | Policy | Owner | Other user | Anon |
|---|---|---|---|---|
| documents | select own | allow | deny | deny |

## Production
- Applied: <yes on confirmation | pending confirmation | not requested>
- Backup confirmed: <yes / path>
- Post-apply integrity: <result>
```

## RLS patterns (Postgres / Supabase)

```sql
alter table documents enable row level security;
alter table documents force row level security;   -- owner does not bypass

create policy "read own" on documents for select
  using (auth.uid() = user_id);
create policy "write own" on documents for insert
  with check (auth.uid() = user_id);
```

Test every policy from three roles: **owner allowed, other user denied, anonymous denied.** A policy
that is present but never tested from a non-owner perspective is not verified. `FORCE ROW LEVEL
SECURITY` matters: without it the table owner (and anything connecting as the owner role) bypasses
every policy, which is a silent hole.

## History

`.db-reports/history.json`: migrations applied per environment, and `patterns_observed` for
drift causes that recur (a specific console habit, an env that always lags).

## SITREP

Drift first with its resolution, then the migration with its reversibility and data-risk, then RLS
verification, then the production gate status. A `/db` run that touched production without recording
the confirmation and the backup is not done.

### Suggested next

| Outcome | Recommend |
|---|---|
| Migration proved, ready for prod | confirm, then `/gh-ship` the migration files |
| Drift was a code bug | `/test-ship` - a test would have caught the reference |
| RLS added or changed | `/redteam --class authz` locally, or `/sec-ship` Agent 4 |
| Schema change is a real design decision | `/mdmp` before committing to it |

## Design notes

**Introspect the database, not the files.** Migration files are intent; the live schema is reality;
drift is the gap. Reading only the files makes drift invisible, which is exactly when it bites.

**Prove the down migration.** "Reversible" is the most over-claimed word in migrations. Running the
`down` and checking it restored state is the difference between a rollback and a hope.

**Expand/contract over destructive.** Additive-then-cleanup keeps every step reversible and every
deploy safe, at the cost of two migrations instead of one. That trade is almost always right for a
table with data in it.

**Production is always a question, never a default.** The one rule that, on its own, prevents the
worst outcome this skill exists to avoid.
