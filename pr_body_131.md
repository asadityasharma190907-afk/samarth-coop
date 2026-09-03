## Summary

This PR implements the missing endpoints for the Cooperative Admin verification workflow, satisfying Story 6.4 (Issue #131). This allows admins to query for pending workers and accept/reject them, forming the backend core of the Federation Dashboard's verification queue.

## Approach Taken
1. **Schema Enhancements**: 
   - Added `AdminWorkerItemResponse` in `backend/app/schemas/admin.py` to seamlessly serialize the join of `User` and `WorkerProfile`.
2. **Service Layer**:
   - Renamed `toggle_verification()` to `update_verification_status()` for clarity.
   - Built `get_workers_by_status()` to execute a standard inner join between `WorkerProfile` and `User`, returning exactly the fields specified by the PM.
3. **Admin Routing**:
   - Added `GET /admin/workers?status=pending` using the newly minted schema and service function.
   - Refactored `PATCH /admin/workers/{id}/verify` to use the updated service function name and dynamic response messaging.

## Testing
- Extended `backend/tests/test_admin.py` to cover:
  - Valid `GET` queries for `"pending"` and `"verified"` statuses.
  - Ensuring non-admins natively get a `403 Forbidden` response.
- `pytest backend/` test suite runs successfully with **75 tests passing**.

Closes #131
