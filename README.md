# CANUMPE Academic API

A read-only REST API that lets an authenticated student retrieve their own academic
information, aggregated from independent source systems (Moodle, Attendance). Students
consume the API from their own applications; the API returns structured JSON facts, not
reports or dashboards.

## Status

This repository currently implements one full vertical slice end-to-end, as a template
for the rest of the API:

- API key authentication (`Authorization: Bearer <key>`)
- `GET /api/v1/me/attendance` — the authenticated student's attendance history, read
  from the Attendance PostgreSQL database
- `GET /health`, `GET /ready`
- The API's own database (API key metadata + student identity mapping), managed with
  Alembic

Moodle integration, additional `/me/*` endpoints, and teacher/admin roles are not yet
implemented — see the engineering instructions this project follows for the full scope.

## Architecture

Four concerns are kept separate, matching `app/`:

```
app/api/         HTTP layer: routes, request/response wiring, error shaping
app/auth/        API key parsing, hashing, verification, the auth dependency
app/semantic/    Source-agnostic domain model (e.g. AttendanceRecord)
app/repositories/ Source-specific SQL, isolated per source system
app/services/    Glue between repositories and the semantic model
app/schemas/     Pydantic response models (the public contract)
app/models/      SQLAlchemy models for the API's OWN database only
app/db/          Engine/session setup — one for the API's own DB, one per source DB
app/core/        Settings, logging
```

The public API never exposes source-system table or column names. A repository is the
only place allowed to know about `students`, `attendance_sessions`, etc.

## Local development

Requires Docker and Python 3.12+.

1. Start disposable Postgres containers (an API metadata DB and a fake Attendance DB
   pre-seeded with fixture data — see `tests/fixtures/`):

   ```
   docker compose -f compose.test.yml up -d
   ```

2. Create a virtualenv and install the project with dev dependencies:

   ```
   python3 -m venv .venv
   .venv/bin/pip install -e ".[dev]"
   ```

3. Copy `.env.example` to `.env` and point it at the containers above (ports `5433`
   for the API DB, `5434` for the Attendance DB), or export the equivalent environment
   variables directly:

   ```
   export API_DB_URL=postgresql+psycopg://test:test@localhost:5433/canumpe_academic_api_test
   export ATTENDANCE_DB_URL=postgresql+psycopg://test:test@localhost:5434/asistencia_test
   export API_KEY_HASH_PEPPER=dev-pepper
   ```

4. Run migrations and start the app:

   ```
   .venv/bin/alembic upgrade head
   .venv/bin/uvicorn app.main:app --reload
   ```

5. Open http://localhost:8000/docs for interactive OpenAPI documentation.

### Issuing a test API key

There is no admin endpoint yet. Issue one directly against the API database:

```python
from app.db.api_db import get_sessionmaker
from app.models.student import StudentIdentity
from app.models.api_key import ApiKey
from app.auth.api_key import generate_api_key, hash_secret

session = get_sessionmaker()()
student = StudentIdentity(account_number="A0001")  # must match a real account_number
session.add(student)
session.flush()

plaintext, key_id, secret = generate_api_key()
session.add(ApiKey(key_id=key_id, key_hash=hash_secret(secret, "dev-pepper"), student_id=student.id))
session.commit()
print(plaintext)  # shown once -- only the hash is stored
```

Use it as `Authorization: Bearer <plaintext>`.

## Running tests

```
.venv/bin/pytest            # unit + integration + API tests
.venv/bin/ruff check .
.venv/bin/mypy app
```

Integration and API tests automatically skip if the containers from step 1 above
aren't running.

## Deployment

Production never builds source code. It only pulls a pre-built image from GHCR:

```
docker compose pull
docker compose up -d
```

`compose.yml` runs three things: the API's own Postgres database, a one-shot `migrate`
service (`alembic upgrade head`), and the API itself. `ATTENDANCE_DB_URL` (and, later,
`MOODLE_DB_URL`) must point at the existing source systems — this compose file does not
create them. See `.env.example` for required variables.

Roll back by changing `TAG` to a previous image tag and re-running `docker compose pull
&& docker compose up -d`.

See `SECURITY.md` for the security model and `AI_INSTRUCTIONS.md` for the engineering
rules this codebase is built and reviewed against.
