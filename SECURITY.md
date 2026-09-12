# Security model

## Authentication

Students authenticate with an individual API key sent as `Authorization: Bearer <key>`.

A key has the shape `cnp_<key_id>_<secret>`:

- `key_id` (16 hex chars) is a public, indexed lookup value.
- `secret` (32 random bytes, URL-safe encoded) is never stored. Only
  `SHA-256(pepper + secret)` is persisted, in `api_keys.key_hash`.
- `API_KEY_HASH_PEPPER` is a server-side secret mixed into every hash. Rotating it
  invalidates every issued key at once — treat it like a master key, not a per-key
  value.

Verification uses `hmac.compare_digest` for constant-time comparison. A key can be
revoked by setting `api_keys.revoked_at`; revoked and unknown keys are indistinguishable
to the caller (both return a generic 401).

Keys are never logged in full. Only `key_id` (public, non-secret) and the internal
student id are attached to request logs.

## Authorization

`GET /api/v1/me/*` endpoints derive the student entirely from the authenticated API
key via `get_current_student`. No endpoint accepts an account number, student id, or
any other identity claim from the client for its own `/me` data — there is currently no
code path that resolves a student from a client-supplied identifier for these routes,
which is what prevents Student A from ever retrieving Student B's data by editing a URL
or payload.

Role is stored on `student_identities.role` (`student`, `teacher`, `admin`) for future
use; no endpoint currently branches on it.

## Data access

The API is read-only against both Moodle and the Attendance database. Repositories
(`app/repositories/`) contain 100% of the SQL run against those source systems, and
issue only `SELECT` statements. Production credentials for those connections must be
PostgreSQL roles granted `SELECT` only, never write access.

The API's own database (`API_DB_URL`) stores API key metadata and the student identity
mapping — never a copy of academic records.

## Error responses

All errors return `{"error": "<slug>", "message": "<human readable>"}` with an
appropriate status code. Unhandled exceptions are caught, logged server-side with a
stack trace, and returned to the client as a generic `500 internal_error` with no
details about the underlying failure.

## Secrets

Never commit `.env`, database credentials, or `API_KEY_HASH_PEPPER`. `.env.example`
contains variable names and placeholder values only. The application never logs secret
values or full `Authorization` headers.

## Reporting a vulnerability

If you find a security issue in this project, please report it privately to the
maintainer rather than opening a public issue.
