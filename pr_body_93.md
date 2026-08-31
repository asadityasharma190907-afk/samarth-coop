### Summary
This PR implements **[Story 5.2] Citizen Rating API**, allowing a citizen to rate a worker 1-5 stars for a completed booking. This rating actively feeds back into the worker's dispatch score by maintaining a running average of their ratings.

### Approach
- **Database Schema**: Added `rating_count` (Integer, default 0) to `worker_profiles` to easily calculate the running average without full table scans on `bookings`. Added `rating` (Integer, nullable) to `bookings` to record the rating and prevent double-rating. 
- **Migration**: Generated Alembic migration `c56d8283c0f0_story_5_2_rating_api` to add these columns.
- **Service & Router**: Implemented `POST /bookings/{id}/rating` expecting a `RatingRequest` (1-5 integer). The service `submit_rating()` validates that the job is completed and not yet rated, calculates the new running average, and updates both the profile and the booking.

### Testing
- Added tests in `backend/tests/test_bookings.py`:
  - ✅ `test_rate_booking_success`: Simulates a full create -> accept -> complete -> rate flow, asserting the running average updates correctly.
  - ✅ `test_rate_booking_invalid_value`: Tests 422 Validation Error when passing ratings outside the 1-5 range.
  - ✅ `test_rate_booking_double_rating`: Tests 409 Conflict when rating a booking that is already rated.
  - ✅ `test_rate_booking_uncompleted`: Tests 400 Bad Request when attempting to rate a pending/assigned booking.
  - ✅ `test_rate_booking_unauthorized`: Tests 404 Not Found when a citizen tries to rate a booking that doesn't exist or isn't theirs.
- All tests pass locally using `pytest tests/test_bookings.py -k rating -v`.

Closes #93
