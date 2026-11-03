# PostgreSQL Setup

Every module's backends read from a PostgreSQL database named `taskboard`. You
need it running before you start any backend.

Commands are shown for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)**. Pick the pair that matches your machine.

## Option A — Docker (recommended, no local install)

**macOS / Linux**

```bash
docker run -d --name taskboard-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=taskboard \
  -p 5432:5432 \
  postgres:16
```

**Windows (PowerShell)** — use backticks for line continuation, or put it on
one line:

```powershell
docker run -d --name taskboard-db `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=taskboard `
  -p 5432:5432 `
  postgres:16
```

Stop / start it later (same on both platforms):

```
docker stop taskboard-db
docker start taskboard-db
```

Connection values for your `.env`:

```
Host=localhost  Port=5432  Database=taskboard  Username=postgres  Password=postgres
```

## Option B — Local install

| Platform | Install | Notes |
|----------|---------|-------|
| macOS | `brew install postgresql@16 && brew services start postgresql@16` | `psql` is on `PATH` via Homebrew |
| Linux (Debian/Ubuntu) | `sudo apt install postgresql-16` | service starts automatically; connect as the `postgres` user |
| Windows | `winget install PostgreSQL.PostgreSQL.16` or the EnterpriseDB installer | add `C:\Program Files\PostgreSQL\16\bin` to `PATH` so `psql` works in a new terminal |

Then create the database:

```
createdb taskboard
```

or, if `createdb` is not on `PATH`:

```
psql -U postgres -c "CREATE DATABASE taskboard;"
```

## Applying the schema

The SQL files in each module's `database/` folder are the **single source of
truth** for the schema.

### With a local `psql` (any platform)

```
cd labs/module-01
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -f database/schema.sql
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -f database/seed.sql
```

The connection URL and `-f` flag work identically in bash and PowerShell.

### With the Docker container and no local `psql`

**macOS / Linux**

```bash
docker exec -i taskboard-db psql -U postgres -d taskboard < database/schema.sql
docker exec -i taskboard-db psql -U postgres -d taskboard < database/seed.sql
```

**Windows (PowerShell)** — `<` input redirection is not supported; pipe instead:

```powershell
Get-Content database/schema.sql | docker exec -i taskboard-db psql -U postgres -d taskboard
Get-Content database/seed.sql   | docker exec -i taskboard-db psql -U postgres -d taskboard
```

`seed.sql` is safe to re-run — it truncates and reloads the sample rows.

## Verifying

```
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -c "SELECT id, title, status FROM tasks ORDER BY id;"
```

You should see six seeded tasks across the three statuses. (Docker-only: prefix
with `docker exec -i taskboard-db ` and drop the connection URL.)

## Later modules

Schema changes arrive as **new numbered files** under `database/migrations/`
(e.g. `002_add_users.sql`). Apply them in order on top of your existing
database, or drop and recreate from the updated `schema.sql`. Never edit an
already-released migration.
