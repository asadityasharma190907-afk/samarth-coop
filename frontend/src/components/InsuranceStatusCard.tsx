import React from 'react';
import './InsuranceStatusCard.css';

interface InsuranceStatusCardProps {
  completedJobs: number;
  lifetimeContribution: number;
}

export function InsuranceStatusCard({
  completedJobs,
  lifetimeContribution,
}: InsuranceStatusCardProps) {
  const toolLoanThreshold = 100;
  const progressPercent = Math.min((completedJobs / toolLoanThreshold) * 100, 100);

  return (
    <div className="insurance-card">
      <h2>Your Cooperative Benefits</h2>

      <div className="insurance-section">
        <h3>Health Insurance (Group Policy)</h3>
        <p className="insurance-detail">
          <strong>Status:</strong> Covered via Welfare Fund
        </p>
        <p className="insurance-detail">
          <strong>Policy:</strong> New India Assurance &mdash; Group
        </p>
        <p className="insurance-detail">
          <strong>Coverage:</strong> INR 2,00,000 per annum
        </p>
      </div>

      <div className="insurance-section">
        <h3>Your Lifetime Welfare Fund Contribution</h3>
        <p className="insurance-detail">
          INR {lifetimeContribution.toLocaleString('en-IN', { maximumFractionDigits: 2 })} (from{' '}
          {completedJobs} completed jobs)
        </p>
      </div>

      <div className="insurance-section">
        <h3>Tool Loan Eligibility</h3>
        <p className="insurance-detail">Eligible after {toolLoanThreshold} completed jobs</p>
        <p className="insurance-detail">
          You have: {completedJobs} / {toolLoanThreshold} jobs
        </p>
        <div className="progress-container">
          <div
            className="progress-bar"
            style={{ width: `${progressPercent}%` }}
            role="progressbar"
            aria-valuenow={completedJobs}
            aria-valuemin={0}
            aria-valuemax={toolLoanThreshold}
          />
        </div>
        <span className="progress-text">{Math.round(progressPercent)}%</span>
      </div>
    </div>
  );
}
