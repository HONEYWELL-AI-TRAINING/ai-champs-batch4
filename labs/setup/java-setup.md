# Java (Spring Boot) Backend Setup

Each module ships a ready-to-run Spring Boot app under `backend-java/`. You do
not scaffold it — this note covers how to run it and how it is wired.

## Layout

```
backend-java/
├── pom.xml                                    # Spring Boot 3.5, Java 21, Maven
└── src/
    ├── main/java/com/honeywell/taskboard/
    │   ├── TaskBoardApplication.java
    │   ├── web/          # controllers + @RestControllerAdvice  (HTTP layer)
    │   ├── service/      # business logic + domain exceptions
    │   ├── repository/   # Spring Data JPA
    │   ├── model/        # @Entity mapped to the existing tasks table
    │   ├── dto/          # request/response records + OpenAPI @Schema
    │   └── config/       # CORS + OpenAPI metadata
    ├── main/resources/application.yml
    └── test/java/...     # JUnit 5 + Mockito + standalone MockMvc (no DB needed)
```

## First run

Build and test are platform-independent — run them from `backend-java/`:

```
cd labs/module-01/backend-java
mvn test           # compiles + runs the unit tests (no database needed)
```

> **No `mvn` on your machine?** A Maven wrapper is bundled — use `./mvnw test`
> on macOS/Linux or `.\mvnw.cmd test` on Windows. It downloads the pinned
> Maven version on first use, so everything below works with `mvnw` in place
> of `mvn` too.

Running the API needs PostgreSQL up and the schema applied. Spring Boot binds
the three `SPRING_DATASOURCE_*` environment variables automatically:

**macOS / Linux (bash/zsh)**

```bash
export SPRING_DATASOURCE_URL="jdbc:postgresql://localhost:5432/taskboard"
export SPRING_DATASOURCE_USERNAME=postgres
export SPRING_DATASOURCE_PASSWORD=postgres
mvn spring-boot:run
```

**Windows (PowerShell)**

```powershell
$env:SPRING_DATASOURCE_URL = "jdbc:postgresql://localhost:5432/taskboard"
$env:SPRING_DATASOURCE_USERNAME = "postgres"
$env:SPRING_DATASOURCE_PASSWORD = "postgres"
mvn spring-boot:run
```

The API listens on `http://localhost:8080`.

- Swagger UI — `http://localhost:8080/swagger-ui.html`
- OpenAPI JSON — `http://localhost:8080/v3/api-docs`
- Health — `http://localhost:8080/health`

## Key conventions

- **`spring.jpa.hibernate.ddl-auto=none`** — `database/schema.sql` owns the
  schema; Hibernate never alters it.
- **Controller → Service → Repository**, same as the other backends.
- `created_at` / `updated_at` are database-managed; the entity marks them
  `@Generated` and the service uses `saveAndFlush` so the response carries the
  real values.
- CORS is locked to the Vite dev server origin (`FRONTEND_ORIGIN`, default
  `http://localhost:5173`).

## See also

- [.NET backend setup](dotnet-setup.md)
- [Python (FastAPI) backend setup](python-setup.md)
