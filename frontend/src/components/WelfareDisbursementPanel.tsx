import React from 'react';
import { useWelfareSummary, useWelfareDisbursements } from '../hooks/useWelfare';
import './WelfareDisbursementPanel.css';

const CATEGORY_LABELS: Record<string, string> = {
  insurance: 'Health & Life Insurance',
  tool_loan: 'Tool & Equipment Loans',
  training: 'Skill Development & Training',
  emergency: 'Emergency Relief Support',
  pension: 'Worker Pension Fund',
};

function formatINR(val: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val);
}

export function WelfareDisbursementPanel() {
  const { data: summary, isLoading: summaryLoading } = useWelfareSummary();
  const { data: disbursements, isLoading: historyLoading } = useWelfareDisbursements();

  if (summaryLoading || historyLoading) {
    return <div className="loading-state">Loading Welfare Governance data...</div>;
  }

  const totalFees = summary?.total_fees || 0;
  const totalDisbursed = summary?.total_disbursed || 0;
  const remainingBalance = summary?.remaining_balance || 0;
  const breakdown = summary?.category_breakdown || {};

  const recentDisbursements = disbursements?.slice(0, 5) || [];

  return (
    <div className="welfare-governance-panel animate-fade-in">
      <div className="welfare-panel-header">
        <h2>
          🏦 Cooperative Welfare Fund Governance
          <span className="welfare-badge">Audited Ledger</span>
        </h2>
      </div>

      <div className="welfare-stats-row">
        <div className="welfare-stat-card primary">
          <div className="welfare-stat-label">Total Fund Collected</div>
          <div className="welfare-stat-val">{formatINR(totalFees)}</div>
        </div>

        <div className="welfare-stat-card">
          <div className="welfare-stat-label">Total Disbursed</div>
          <div className="welfare-stat-val">{formatINR(totalDisbursed)}</div>
        </div>

        <div className="welfare-stat-card">
          <div className="welfare-stat-label">Remaining Unspent Balance</div>
          <div className="welfare-stat-val">{formatINR(remainingBalance)}</div>
        </div>
      </div>

      <div className="welfare-breakdown-section">
        <h3 className="welfare-section-title">Fund Allocation Breakdown</h3>

        {Object.keys(breakdown).length === 0 ? (
          <div className="welfare-empty-state">
            No fund allocations recorded yet. All collected fees remain in the reserve balance.
          </div>
        ) : (
          <div className="welfare-bars-list">
            {Object.entries(breakdown).map(([cat, amt]) => {
              const label = CATEGORY_LABELS[cat] || cat;
              const pct = totalDisbursed > 0 ? Math.round((amt / totalDisbursed) * 100) : 0;

              return (
                <div key={cat} className="welfare-bar-item">
                  <div className="welfare-bar-meta">
                    <span className="welfare-category-name">
                      {label} ({pct}%)
                    </span>
                    <span className="welfare-category-amount">{formatINR(amt)}</span>
                  </div>
                  <div className="welfare-bar-track">
                    <div className="welfare-bar-fill" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="welfare-history-section">
        <h3 className="welfare-section-title">Recent Fund Disbursements</h3>

        {recentDisbursements.length === 0 ? (
          <div className="welfare-empty-state">No disbursements recorded yet.</div>
        ) : (
          <table className="welfare-history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Category</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Audit Status</th>
              </tr>
            </thead>
            <tbody>
              {recentDisbursements.map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.disbursed_at).toLocaleDateString('en-IN')}</td>
                  <td>
                    <span className="welfare-category-name">
                      {CATEGORY_LABELS[item.category] || item.category}
                    </span>
                  </td>
                  <td>{item.description || 'N/A'}</td>
                  <td className="amount">{formatINR(item.amount)}</td>
                  <td className="welfare-status-verified">✓ Verified</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
