## Summary

This PR adds a comprehensive end-to-end test to verify the lazy offer expiry cascade behavior (Story 6.2). It simulates a scenario where workers ignore an offer until it passes its `expires_at` timestamp, ensuring that subsequent read requests lazily mark the offer as expired and automatically cascade the job to the next-ranked worker.

### Bug Fixes Included
While implementing the test, a bug was discovered in `backend/app/routers/offers.py` (`GET /booking-offers/worker`). It was only applying lazy expiration to offers already belonging to the *current* worker. This prevented the global cascade from working when a new worker checked their app. I fixed this by applying a global check for expired active offers first.

## Approach Taken
- Created `test_lazy_expiry.py` utilizing the 4 workers from `seed_data()`.
- Simulated citizens booking an electrician.
- Artificially backdated the `expires_at` timestamp on active offers using the database.
- Authenticated sequentially as Rank 2, 3, and 4 workers, calling `GET /booking-offers/worker` to trigger the lazy cascade.
- Validated that offers are correctly marked as `expired`, new offers generated with incremented `rank_at_offer`, and ultimately transitioned the booking to `cancelled` upon exhaustion.

## Testing
- `pytest backend/tests/test_lazy_expiry.py` passes successfully.
- Ran the full test suite (`pytest`) to ensure the global lazy evaluation fix didn't introduce regressions.

Closes #129
