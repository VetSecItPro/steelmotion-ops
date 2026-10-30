# /db - phases in detail

## Phase 1-2: detect and introspect

Detect provider + ORM (`stacks.md`). Introspect the **live** schema of the target environment:
tables, columns, types, constraints, indexes, and RLS policies where supported. Record it as the
baseline. Never trust the migration files as the current state - they are history, not truth.

## Phase 3: drift detection

Compare the live schema against what the code expects (the ORM model, the type definitions, the
migration history). Classify each difference:

- **Schema ahead of code:** a column/table exists that the code does not know about. Usually a
  hand-applied change that was never committed. Capture it into a migration so it stops being drift.
- **Code ahead of schema:** the code references something the database lacks. Either a pending
  migration was not applied, or a genuine bug.
- **Divergent:** the same object differs (a type widened in prod only, an index in one env). The most
  dangerous kind - resolve deliberately, per environment.

## Phase 4: code fix vs schema change (the judgment)

Before generating a migration, ask whether the schema is what is wrong. If the code queries a column
that should not exist, fix the query - reversible, no data risk. Alter the schema only when the schema
is genuinely incorrect. **A schema change made to accommodate a bug bakes the bug into the database**,
where it is far harder to undo than a code change.

## Phase 5: generate the migration

Reversible by construction. The `up` makes the change; the `down` restores the prior state exactly.
Where a change is genuinely irreversible (dropping a column with data), say so explicitly, require
confirmation, and pair it with a backup step - never a silent one-way door.

Prefer the expand/contract pattern for anything touching existing data:
1. **Expand:** add the new structure, nullable or defaulted, non-breaking
2. **Backfill:** migrate data in a separate, resumable step
3. **Contract:** remove the old structure only once nothing reads it

Every migration carries a WHY comment - what changed and the reason, for the next reader.

## Phase 6: prove locally, both directions

Run `up`, verify the intended state. **Then run `down`, and verify it restored the prior state.** A
`down` that has never been run is a claim, not a rollback. Then `up` again to leave the local DB in the
target state. Only after both directions are proven is the migration fit to recommend for production.

## Phase 7: validate integrity

After applying: constraints satisfied, foreign keys intact, no orphaned rows, counts as expected, RLS
still enforced. A migration that succeeds structurally but corrupts a relationship is a failure.

## Phase 8: regenerate types

Run the stack's type generation. Confirm the type layer now matches the schema - a stale type file is
a lie the compiler will believe.

## Phase 9: production

Never automatic. Present: the migration, its rollback, the local proof, the data-risk assessment, and
the backup status. **Ask.** Apply to production only on explicit confirmation, and re-validate
integrity after.
