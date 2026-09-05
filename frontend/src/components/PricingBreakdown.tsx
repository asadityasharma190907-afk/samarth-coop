import React from 'react';
import { Booking } from '../hooks/useBooking';
import './PricingBreakdown.css';

interface PricingBreakdownProps {
  booking: Booking;
}

export function PricingBreakdown({ booking }: PricingBreakdownProps) {
  if (!booking.is_surging) {
    return null;
  }

  const basePrice = booking.base_price ?? booking.job_price;
  const surplus = booking.surge_surplus ?? (booking.job_price - basePrice);
  const workerExtra = Math.round(surplus * 0.70);
  const workerBaseEarnings = Math.round(basePrice * 0.95);
  const workerTotalEarns = workerBaseEarnings + workerExtra;
  const welfareExtra = Math.round(surplus * 0.20);

  const urgencyLabel =
    booking.urgency === 'emergency'
      ? 'Emergency (+35%)'
      : booking.urgency === 'urgent'
      ? 'Urgent (+20%)'
      : 'High Demand';

  return (
    <div className="pricing-breakdown-card">
      <div className="pricing-breakdown-header">
        <span className="pricing-breakdown-icon">💡</span>
        <span className="pricing-breakdown-title">Fair-Surge Pricing Active</span>
      </div>

      <div className="pricing-breakdown-body">
        <div className="pricing-row">
          <span className="pricing-label">Base rate</span>
          <span className="pricing-value">₹{basePrice}</span>
        </div>

        <div className="pricing-row surge-row">
          <span className="pricing-label">Surge premium ({urgencyLabel})</span>
          <span className="pricing-value surge-value">+₹{surplus}</span>
        </div>

        <div className="pricing-divider" />

        <div className="pricing-row total-row">
          <span className="pricing-label total-label">You pay</span>
          <span className="pricing-value total-value">₹{booking.job_price}</span>
        </div>

        <div className="pricing-row worker-row">
          <span className="pricing-label">Worker earns</span>
          <span className="pricing-value worker-value">
            ₹{workerTotalEarns} <span className="pricing-subtext">(+₹{workerExtra} extra)</span>
          </span>
        </div>

        <div className="pricing-row welfare-row">
          <span className="pricing-label">Welfare Fund</span>
          <span className="pricing-value welfare-value">+₹{welfareExtra}</span>
        </div>
      </div>
    </div>
  );
}
