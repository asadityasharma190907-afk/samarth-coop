### Summary
This PR introduces the `PATCH /admin/workers/{id}/verify` endpoint, allowing users with the `admin` role to toggle the `verified` status of worker profiles. Unverified workers are automatically excluded from the citizen dispatch pool (`GET /workers`), ensuring only cooperative-endorsed workers receive jobs.

### Approach
1. **Schema**: Added `WorkerVerificationUpdate` to parse the JSON boolean payload.
2. **Service**: Implemented `toggle_verification()` to find a profile by `user_id` and update its `verified` flag (throws 404 if not found).
3. **Router**: Built the `PATCH` endpoint, protected by `get_current_user` checking for `user.role == "admin"` (throws 403 Forbidden otherwise).
4. **Seed Data**: Added a default admin user to `seed.py` (Phone: `9000000000`, Password: `password123`) to facilitate manual testing.

### Testing
- ✅ **Unit/Integration**: Added a comprehensive suite in `test_admin.py` covering:
  - 403 Forbidden for non-admin tokens (citizen/worker)
  - Successful toggling (`True`/`False`) by an admin
  - 404 Not Found for invalid worker IDs
  - E2E dispatch check: verifying that unverified workers do not appear in `GET /workers` results.
- ✅ All tests pass locally via `pytest`.

### Notes for Reviewer
- The `GET /workers` exclusion logic was already partially supported in `dispatch.py` via the `verified == True` filter, so this PR seamlessly hooks into that existing logic.
- An admin user was added to `seed.py` — please ensure this aligns with your data seeding strategy.

Closes #92
