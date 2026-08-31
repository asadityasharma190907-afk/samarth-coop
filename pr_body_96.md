### Summary
This PR implements **[Story 5.5] Federation Dashboard UI — Ministry/NCCT View**. It introduces a dedicated read-only dashboard allowing evaluators to monitor live statistics, view recent bookings, and inspect the algorithm's dispatch decisions.

### Changes Made
- **Backend API**: 
  - Created a new `federation.py` router with two new endpoints: 
    - `GET /federation/stats`: Aggregates the total registered workers, completed bookings, and the Cooperative Welfare Fund total.
    - `GET /federation/bookings`: Returns a list of recent platform bookings.
- **Frontend Components**:
  - `StatCounter.tsx`: Built an animated numerical counter for the statistics, applying the specific violet gradient for the Welfare Fund as requested.
  - `AuditTable.tsx`: Added an elegant table component that fetches and renders the audit trail for a selected booking, strictly utilizing monospace (`var(--font-mono)`) for dispatch scores to emphasize transparency.
  - `Federation.tsx`: The primary `/federation` dashboard layout combining the stat counters, recent bookings list, and the audit trail table view.

Closes #96
