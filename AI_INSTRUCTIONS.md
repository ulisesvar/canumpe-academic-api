# CANUMPE Academic API — Engineering Instructions

You are working on the CANUMPE Academic API, an educational but production-quality REST API.

The project will expose academic information to students through individual API keys.

Students will consume the API from applications they create themselves. The API must return structured data, primarily JSON. It must not create the student's report, dashboard, or presentation for them.

## Primary outcome

Provide a secure, simple, well-documented API that allows an authenticated student to retrieve only their own academic information from multiple source systems.

Initial sources:

1. Moodle PostgreSQL database.
2. Attendance PostgreSQL database.

The API is read-only against both source systems.

---

# Technology

Use:

* Python 3.12+
* FastAPI
* Pydantic
* SQLAlchemy 2.x where appropriate
* psycopg 3 for PostgreSQL connectivity
* Alembic for the API's own database migrations
* pytest
* HTTPX / FastAPI TestClient
* Ruff
* mypy where practical
* Docker
* Docker Compose
* GitHub Actions
* GitHub Container Registry (GHCR)

Do not introduce frameworks or infrastructure unless they solve an actual requirement.

Prefer simplicity over architectural sophistication.

---

# Runtime architecture

The application must run entirely inside a Docker container.

Production servers must NOT require:

* Python installation
* pip
* Poetry
* virtualenv
* Node.js
* npm
* source code checkout
* compilation
* docker build
* application dependencies installed on the host

The production host should require only:

* Docker Engine
* Docker Compose
* access to the container registry
* compose.yml
* environment/secrets configuration

Deployment must work with:

docker compose pull
docker compose up -d

The production server must pull a pre-built container image from:

ghcr.io/<owner>/canumpe-academic-api:<tag>

The application image must be built by GitHub Actions, not on the production server.

---

# Repository structure

Prefer a structure similar to:

app/
main.py
api/
routes/
auth/
models/
schemas/
services/
repositories/
db/
semantic/
core/

tests/
unit/
integration/
api/

alembic/

.github/
workflows/
ci.yml
release.yml

Dockerfile
compose.yml
compose.test.yml
.env.example
.gitignore
.dockerignore
pyproject.toml
README.md
SECURITY.md
AI_INSTRUCTIONS.md

Do not create unnecessary layers merely to conform to this example.

---

# Architecture principles

Keep four concerns separated:

1. API / HTTP layer
2. Authentication and authorization
3. Semantic/domain model
4. Source data access

The public API must never expose Moodle's internal database schema or attendance database schema.

Create a semantic/domain layer representing concepts such as:

* Student
* Course
* Assignment
* Grade
* Attendance
* Participation

Source-specific SQL must remain isolated inside repository/data-access components.

For example:

Moodle tables
↓
Moodle repository
↓
semantic/domain model
↓
API schema
↓
JSON

Do not leak names such as mdl_grade_grades or internal attendance table structures into the public contract.

---

# Authentication

Students authenticate using individual API keys.

Requests use:

Authorization: Bearer <API_KEY>

The API key identifies the student.

Endpoints using /me must derive the student identity from the authenticated API key.

Never accept an account number from the client when accessing /me resources.

Example:

GET /api/v1/me/attendance

must determine the student internally from the API key.

A student must never be able to obtain another student's data by changing a URL parameter.

API keys must:

* contain sufficient cryptographic entropy
* never be stored in plaintext in the API database
* be stored using a secure hash
* support revocation
* support regeneration
* optionally have last_used_at
* have an internal identifier suitable for audit logs

Never write complete API keys to logs.

---

# Authorization

Initial roles:

student
teacher
admin

Students may access only their own resources.

Teachers and administrators may receive additional endpoints later.

Do not implement future functionality until required, but keep the design extensible.

Authorization must be enforced server-side.

Never trust:

* account_number provided by the client
* student_id provided by the client
* UI restrictions
* JavaScript checks

---

# Source databases

The API reads from:

Moodle PostgreSQL
Attendance PostgreSQL

These systems remain independent systems of record.

Do NOT merge their databases.

Do NOT perform writes against either database.

Production credentials used by the API must be PostgreSQL users with SELECT-only privileges.

Prefer separate credentials:

academic_api_moodle
academic_api_attendance

These accounts must have only the permissions required to read the necessary objects.

The API may have its own PostgreSQL database for:

* API key metadata
* student identity mapping
* API configuration
* audit metadata

Do not duplicate Moodle grades or attendance records into the API database unless a future requirement clearly justifies ETL or caching.

Initial architecture should query source systems directly.

---

# Semantic layer

Create a lightweight semantic/domain layer.

Example concepts:

Student
Course
Grade
Assignment
AttendanceRecord

The semantic model should normalize inconsistencies between source systems.

For example:

Moodle internal grade records
↓
Grade

Attendance database records
↓
AttendanceRecord

The public API contract must remain stable even if internal source queries change.

---

# API design

Use versioned routes:

/api/v1/

Initial candidate endpoints:

GET /api/v1/me
GET /api/v1/me/courses
GET /api/v1/me/grades
GET /api/v1/me/assignments
GET /api/v1/me/attendance

Do not implement an endpoint until its use case and data source are understood.

Prefer RESTful resource representations.

Use JSON as the canonical initial representation.

Do not create processed reports for students.

Return the underlying academic facts in a clean semantic representation so students can build their own reports.

---

# OpenAPI documentation

FastAPI OpenAPI documentation must remain enabled.

Provide useful:

* endpoint descriptions
* request examples
* response examples
* schemas
* authentication documentation
* error responses

Swagger/OpenAPI is part of the product and not merely developer documentation.

---

# Testing requirements

Every new feature must include automated tests.

At minimum include:

## Unit tests

Test:

* API key parsing
* API key hashing/validation
* authorization logic
* semantic transformations
* calculations
* validation
* domain services

## Integration tests

Test against disposable PostgreSQL containers or isolated test databases.

Never run automated tests against production Moodle or production Attendance databases.

## API tests

Test HTTP behavior.

For each protected endpoint test at least:

* valid API key → 200
* missing API key → 401
* malformed API key → 401
* invalid API key → 401
* revoked API key → 401
* correct response schema
* empty data scenario
* dependency/database failure behavior

Authorization tests are mandatory.

Tests must prove that Student A cannot retrieve Student B's data.

Authentication and authorization code should receive particularly strong coverage.

Aim for approximately 80%+ overall coverage where useful, but prioritize meaningful behavioral tests rather than pursuing coverage as a vanity metric.

---

# Sandbox

Development and automated tests must use sandbox infrastructure.

Use Docker Compose to provide disposable dependencies.

Production databases must never be used as development databases.

Provide:

compose.test.yml

or equivalent tooling to create:

academic_api_test_db
mock/test Moodle data
mock/test Attendance data

Fixtures must use fake students and fake academic information.

Do not place real student academic information in GitHub.

---

# Security

Follow least privilege.

The application container must:

* run as a non-root user
* not run privileged
* not mount /var/run/docker.sock
* not mount host system directories
* not contain production secrets
* expose only necessary ports

Never commit:

* .env
* database passwords
* API keys
* Telegram tokens
* private certificates
* production credentials

Provide:

.env.example

containing variable names and safe examples only.

Use environment variables or external secrets for runtime configuration.

Do not print secrets during application startup.

---

# Logging

Produce structured application logs.

Useful fields include:

* timestamp
* request_id
* endpoint
* HTTP method
* response status
* duration
* internal API key identifier
* internal student identifier when appropriate

Never log:

* complete API keys
* database passwords
* Authorization headers
* secrets

Avoid logging unnecessary student personal information.

---

# Rate limiting

Design for rate limiting.

Initial limits may be simple.

A programming mistake from a student must not be able to generate unlimited requests or exhaust server resources.

Return appropriate HTTP status codes such as 429 when applicable.

---

# Database migrations

Use Alembic for the Academic API's own database.

Never require manual CREATE TABLE or ALTER TABLE commands in production as the normal deployment procedure.

Migrations must be version controlled.

Migrations must never alter Moodle or Attendance schemas.

---

# Git workflow

main must remain deployable.

Changes should normally be created on feature branches:

feature/<description>
fix/<description>

Merge through pull requests.

Do not commit generated secrets or environment-specific configuration.

---

# Continuous integration

Every pull request must automatically perform:

1. dependency installation inside CI
2. linting
3. static/type checks where applicable
4. unit tests
5. integration tests
6. API tests
7. security checks
8. container build verification

Failure of required tests must block acceptance.

---

# Container publishing

A release workflow must:

1. run required tests
2. build the Docker image
3. tag the image
4. publish it to GHCR

Suggested tags:

latest
v1.0.0
git-<short-sha>

Production should preferably deploy an immutable version tag rather than relying exclusively on latest.

Example:

ghcr.io/<owner>/canumpe-academic-api:v1.0.0

---

# Production deployment

Production must NOT build source code.

The server receives only operational configuration such as:

/opt/canumpe/apps/academic-api/
compose.yml
.env

Deployment:

docker compose pull
docker compose up -d

Rollback should be possible by changing the image tag to the previous known-good version and running:

docker compose pull
docker compose up -d

---

# Health checks

Implement at least:

GET /health

Consider separating:

/health
/ready

Health checks must not reveal credentials, database URLs, stack traces, or internal configuration.

The Docker image should expose an appropriate health check.

---

# Error handling

Never expose raw stack traces to API consumers in production.

Return consistent error structures.

Example:

{
"error": "unauthorized",
"message": "Invalid or missing API key"
}

Use appropriate HTTP status codes.

---

# Definition of Done

A feature is not complete simply because it works locally.

Every endpoint must satisfy:

* expected behavior implemented
* unit tests written
* integration/API tests where applicable
* authorization verified
* OpenAPI documentation updated
* no secrets introduced
* lint/static checks passing
* Docker image builds successfully
* application runs as non-root
* CI passes

For authentication or authorization changes, include negative security tests.

---

# AI coding rules

You are allowed to generate and modify code, tests, configuration and documentation.

Before implementing a feature:

1. understand the existing architecture
2. inspect relevant tests
3. identify security consequences
4. make the smallest reasonable change

Never:

* disable tests to obtain a green build
* weaken security checks merely to make code work
* hardcode production secrets
* connect tests to production databases
* remove validation without explaining why
* introduce dependencies without a concrete need
* rewrite large working areas unnecessarily
* change public API contracts silently

When a test fails, determine whether the implementation or the test is incorrect.

Do not automatically modify a failing test merely to match newly generated behavior.

Prefer adding regression tests whenever a bug is fixed.

---

# Engineering principle

AI is used to increase development speed.

Tests, security boundaries, reproducible builds and deployment controls determine whether generated code is acceptable.

Optimize for:

simplicity
security
testability
reproducibility
observability
maintainability

Do not optimize for cleverness.
