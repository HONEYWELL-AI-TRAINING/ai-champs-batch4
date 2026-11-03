# Python (FastAPI) Backend Setup

Each module ships a ready-to-run FastAPI app under `backend-python/`. You do
not scaffold it — this note covers how to run it and how it is wired.

## Layout

```
backend-python/
├── main.py                 # FastAPI app + CORS
├── config.py               # settings from the environment
├── database.py             # async SQLAlchemy engine + session dependency
├── routers/                # HTTP layer  (Router -> Service -> Repository)
├── services/               # business logic + domain errors
├── repositories/           # all database access
├── models/                 # SQLAlchemy models mapped to the existing schema
├── schemas/                # Pydantic request/response models
├── requirements.txt
└── tests/                  # pytest (uses an in-memory fake repo — no DB needed)
```

## First run

### 1. Create and activate a virtual environment

**macOS / Linux (bash/zsh)**

```bash
cd labs/module-01/backend-python
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
cd labs/module-01/backend-python
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> If PowerShell blocks the activation script with an execution-policy error,
> run once: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
> then retry. (Command Prompt users: `.venv\Scripts\activate.bat`.)

### 2. Install dependencies (same on every platform)

```
pip install -r requirements.txt
```

The pins are lower bounds so wheels resolve on Python 3.11 through 3.14.

### 3. Run the tests

```
pytest
```

### 4. Run the API

Needs PostgreSQL up and the schema applied.

**macOS / Linux**

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard"
uvicorn main:app --reload
```

**Windows (PowerShell)**

```powershell
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard"
uvicorn main:app --reload
```

The API listens on `http://localhost:8000`. Interactive docs (Swagger UI) are
at `http://localhost:8000/docs`.

## Key conventions

- **No `Base.metadata.create_all()`** — `database/schema.sql` owns the schema.
- **Router → Service → Repository**, same as the other backends.
- The engine is created lazily, so importing the app (for tests) never opens a
  database connection.
- CORS is locked to the Vite dev server origin (`FRONTEND_ORIGIN`, default
  `http://localhost:5173`).

## See also

- [.NET backend setup](dotnet-setup.md)
- [Java (Spring Boot) backend setup](java-setup.md)
