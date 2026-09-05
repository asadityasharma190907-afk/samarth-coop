import React from 'react';
import { useRevenue } from '../hooks/useRevenue';
import { StatCounter } from './StatCounter';
import './RevenueAnalyticsPanel.css';

export function RevenueAnalyticsPanel() {
  const { data, isLoading, error } = useRevenue();

  if (isLoading) {
    return <div className="loading-state">Loading business analytics...</div>;
  }

  if (error || !data) {
    return <div className="error-state">Failed to load revenue analytics.</div>;
  }

  const formatINR = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const maxStreamAmount = Math.max(...data.revenue_streams.map((s) => s.amount));
  const effectiveMax = maxStreamAmount > 0 ? maxStreamAmount : 1;

  return (
    <div className="revenue-analytics-panel">
      <div className="revenue-stats-grid">
        <StatCounter
          label="Gross Merchandise Value (GMV)"
          value={data.gmv}
          prefix="₹"
          isViolet={false}
        />
        <StatCounter
          label="Platform Revenue (This Month)"
          value={data.platform_revenue}
          prefix="₹"
          isViolet={true}
        />
        <StatCounter
          label="Welfare Fund (This Month)"
          value={data.welfare_fund}
          prefix="₹"
          isViolet={false}
        />
      </div>

      <div className="revenue-unit-economics">
        <h3>Unit Economics</h3>
        <div className="unit-economics-row">
          <div className="unit-metric">
            <span className="unit-metric-label">Average Order Value</span>
            <span className="unit-metric-value">{formatINR(data.avg_order_value)}</span>
          </div>
          <div className="unit-metric">
            <span className="unit-metric-label">Blended Fee %</span>
            <span className="unit-metric-value">{data.blended_fee_percentage}%</span>
          </div>
          <div className="unit-metric">
            <span className="unit-metric-label">Net Margin / Booking</span>
            <span className="unit-metric-value">{formatINR(data.net_margin_per_booking)}</span>
          </div>
        </div>

        <div className="revenue-breakeven">
          <div className="breakeven-header">
            <span>Breakeven Target</span>
            <span>
              {data.current_bookings.toLocaleString('en-IN')} /{' '}
              {data.breakeven_target_bookings.toLocaleString('en-IN')} bookings (
              {data.breakeven_percentage}%)
            </span>
          </div>
          <div className="breakeven-progress-track">
            <div
              className="breakeven-progress-fill"
              style={{ width: `${Math.min(data.breakeven_percentage, 100)}%` }}
            />
          </div>
        </div>
      </div>

      <div className="revenue-streams-chart">
        <h3>Revenue Streams</h3>
        <div className="streams-bars-container">
          {data.revenue_streams.map((stream, index) => {
            const heightPct = (stream.amount / effectiveMax) * 100;
            return (
              <div key={index} className="stream-bar-wrapper">
                <div className="stream-bar" style={{ height: `${Math.max(heightPct, 5)}%` }}>
                  <span className="stream-bar-tooltip">
                    {formatINR(stream.amount)} ({stream.percentage}%)
                  </span>
                </div>
                <div className="stream-label">{stream.name}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
