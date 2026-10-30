# /db - provider + ORM detection, per-stack commands

Detect from the repo, never assume. A repo can mix (an app on Postgres+Drizzle with a separate
analytics store). Detect all, handle each.

## Provider

| Signal | Provider |
|---|---|
| `supabase/` dir, `@supabase/*` deps, a `*.supabase.co` URL | Supabase (Postgres + RLS + auth) |
| `postgres://`, `pg`, `postgres` deps, `DATABASE_URL` to 5432 | PostgreSQL |
| `mysql://`, `mysql2`, `planetscale` | MySQL / PlanetScale |
| `*.db`, `better-sqlite3`, `libsql`, Turso | SQLite / libSQL |
| `mongodb://`, `mongoose`, `mongodb` deps | MongoDB |
| `neon`, `@neondatabase/*` | Neon (serverless Postgres) |
| RDS/Aurora endpoint in IaC | AWS-hosted Postgres/MySQL |

## ORM / query layer

| Signal | Layer | Migration command |
|---|---|---|
| `prisma/schema.prisma` | Prisma | `prisma migrate dev` (local), `prisma migrate deploy` (prod), `prisma generate` (types) |
| `drizzle.config.*`, `drizzle/` | Drizzle | `drizzle-kit generate` then `drizzle-kit migrate`; `drizzle-kit push` for dev only |
| `knexfile.*` | Knex | `knex migrate:latest`, `knex migrate:rollback` |
| `kysely` dep + a migrations dir | Kysely | project's own migrator script |
| `supabase/migrations/` | Supabase CLI | `supabase db diff`, `supabase migration new`, `supabase db push` |
| `*.mongoose` schemas | Mongoose | schema-in-code; "migration" = a data script, run once, idempotent |
| raw `.sql` in a migrations dir | hand-rolled | the project's own runner; read it before acting |

**Type generation** differs: Prisma `prisma generate`; Drizzle infers from schema (no step, but
verify the schema file is the source of truth); Supabase `supabase gen types typescript`; Kysely
`kysely-codegen`. Run whichever applies after every schema change (safety rule 6).

## Environments

Identify local, branch/preview, and production connection strings, and **which one every command
would hit.** The most dangerous mistake is running a "local" command against a production
`DATABASE_URL` because the env was set. Confirm the target before any apply. Supabase and Neon branch
databases are the safe place to prove a migration when a pure-local DB is not available.

## Introspect from the database, not the files

The migration files describe what was *intended*; the live schema is what *is*. Drift is the gap
between them, and it is invisible if you only read the files. Introspect the running database
(`\d` / `information_schema` / the ORM's introspect command) and compare against the code's model.
Common drift: a column added by hand in a console, an index created for an incident and never
committed, a type changed in one environment only.
