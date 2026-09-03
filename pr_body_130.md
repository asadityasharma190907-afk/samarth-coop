## Summary

This PR migrates the old `verified` boolean column on `worker_profiles` to a granular `verification_status` string column (`pending`, `verified`, `rejected`), resolving Story 6.3 and Issue #130. This ensures we can properly track workers who are applying vs rejected vs verified, without breaking the core architectural invariant of maintaining exactly 4 MVP tables.

## Approach Taken
1. **Alembic Migration**: Created a migration script that:
   - Adds `verification_status` column.
   - Runs cross-dialect (SQLite + Postgres) `UPDATE` queries to map `verified=True` to `'verified'` and `verified=False` to `'pending'`.
   - Uses Alembic's `batch_alter_table` context to cleanly drop the old `verified` column, ensuring full SQLite support in testing environments.
2. **Schema & Model Updates**: Updated `WorkerProfile` model and the Admin API `PATCH /workers/{id}/verify` endpoint to accept and return the new string-based `verification_status`.
3. **Dispatch Logic**: Updated the dispatch filtering logic to query `WorkerProfile.verification_status == "verified"`.
4. **Seed & Tests**: Updated `app/seed.py` and across **9 test files** to initialize and assert against `verification_status` instead of the old boolean.

## Testing
- Verified `alembic upgrade head` and data migrations work cleanly.
- `pytest backend/` test suite runs successfully with **72 tests passing** against the in-memory SQLite schema utilizing the new migration script.

Closes #130
