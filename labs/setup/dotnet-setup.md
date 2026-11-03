# .NET Backend Setup

Each module ships a ready-to-run .NET 8 solution under `backend-dotnet/`. You
do not scaffold it yourself — but here is how it is wired, because you will
extend it in every module.

## Layout

```
backend-dotnet/
├── TaskBoard.sln
├── src/TaskBoard.Api/            # the Web API project
│   ├── Program.cs
│   ├── Controllers/
│   ├── Services/                 # business logic (ITaskService -> TaskService)
│   ├── Repositories/             # data access (ITaskRepository -> TaskRepository)
│   ├── Data/TaskBoardContext.cs  # EF Core context, mapped to the existing schema
│   └── Models/
└── tests/TaskBoard.Api.Tests/    # xUnit + Moq
```

Because the folder holds a solution **and** project files in different places,
always run `dotnet` commands from `backend-dotnet/` (they resolve
`TaskBoard.sln`), and pass `--project src/TaskBoard.Api` to `dotnet run`.

## First run

Build and test are platform-independent:

```
cd labs/module-01/backend-dotnet
dotnet build          # restore + build the whole solution
dotnet test           # run the unit tests (no database needed)
```

Running the API needs PostgreSQL up and the schema applied, plus the
connection string in the environment. This is the only part that differs by
shell:

**macOS / Linux (bash/zsh)**

```bash
export ConnectionStrings__DefaultConnection="Host=localhost;Port=5432;Database=taskboard;Username=postgres;Password=postgres"
dotnet run --project src/TaskBoard.Api
```

**Windows (PowerShell)**

```powershell
$env:ConnectionStrings__DefaultConnection = "Host=localhost;Port=5432;Database=taskboard;Username=postgres;Password=postgres"
dotnet run --project src/TaskBoard.Api
```

The API listens on `http://localhost:5088`. Swagger UI is at
`http://localhost:5088/swagger` in Development.

> The `__` (double underscore) in the variable name is how .NET maps an
> environment variable onto the nested config key `ConnectionStrings:DefaultConnection`.
> It is not a typo, and it is the same on every OS.

## Key conventions (do not fight these)

- **No EF migrations.** `database/schema.sql` owns the schema. The context
  maps onto existing tables; there is no `EnsureCreated()` call.
- **Controller → Service → Repository.** Controllers only translate HTTP.
  Business rules live in services. All SQL/EF lives in repositories.
- **Interfaces for the seams.** `ITaskService` and `ITaskRepository` exist so
  tests can substitute a Moq double — that is why `dotnet test` needs no
  database.
- **Configuration from the environment.** The connection string comes from
  `ConnectionStrings__DefaultConnection`; nothing sensitive is committed.

## See also

- [Python (FastAPI) backend setup](python-setup.md)
- [Java (Spring Boot) backend setup](java-setup.md)
