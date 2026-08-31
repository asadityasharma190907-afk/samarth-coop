### Summary
This PR implements **[Story 5.3] Offer Audit Trail API**, enhancing `GET /booking-offers/booking/{booking_id}` to return the complete offer cascade history for a booking. This is the primary transparency proof point for Ministry/NCCT evaluators, demonstrating exactly why each worker was chosen and what the outcome was.

### Approach
- **Schema**: Created `AuditTrailEntry` model returning exactly the required fields: `worker_name`, `rank_at_offer`, `dispatch_score`, `status`, and `created_at`.
- **Router**: Updated `get_booking_offers` in `routers/offers.py` to join `BookingOffer` with `User` (to fetch the `worker_name`). The `dispatch_score` is read directly from the stored values in `BookingOffer` to ensure scores are never recomputed, satisfying AD-7.
- **Tests**:
  - Updated `test_get_booking_offers_audit_trail` in `backend/tests/test_bookings.py` to assert the exact structure of `AuditTrailEntry`.
  - Updated `test_lazy_expiry_on_read` in `backend/tests/test_offers.py` to validate `worker_name` instead of raw `worker_id`.
  - Removed unused variable assignment causing lint failures.

All tests (`pytest tests/test_bookings.py tests/test_offers.py`) pass.

Closes #94
