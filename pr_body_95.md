### Summary
This PR implements **[Story 5.4] Rating UI & Society Verified Badge**, adding visual trust signals and user rating interactions to the frontend.

### Changes Made
- **Components Created**:
  - `StarRating.tsx`: Interactive 5-star rating component with hover and selection states.
  - `VerifiedBadge.tsx`: Reusable "Society Verified" green badge matching the design specifications.
- **Pages Updated**:
  - `BookingStatus.tsx`: Added the `VerifiedBadge` to the assigned worker card. Added the `StarRating` section to the job completed state, including the API integration to submit the rating to `POST /bookings/{id}/rating`.
- **Types Updated**: Added the `rating` field to the `Booking` interface in `useBooking.ts` to clear TypeScript errors and accurately reflect backend data.

Closes #95
