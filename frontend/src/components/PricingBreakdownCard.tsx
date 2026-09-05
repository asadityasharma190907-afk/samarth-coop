import React from 'react';
import { PricePreviewData } from '../hooks/usePricePreview';
import './PricingBreakdownCard.css';

interface PricingBreakdownCardProps {
  skillLabel: string;
  locationText: string;
  urgency: 'normal' | 'urgent' | 'emergency';
  onUrgencyChange: (urgency: 'normal' | 'urgent' | 'emergency') => void;
  pricingData?: PricePreviewData;
  isLoading: boolean;
  error?: string | null;
}

export function PricingBreakdownCard({
  skillLabel,
  locationText,
  urgency,
  onUrgencyChange,
  pricingData,
  isLoading,
  error,
}: PricingBreakdownCardProps) {
  return (
    <div className="pricing-breakdown-card" data-testid="pricing-breakdown-card">
      <div className="pricing-breakdown-header">
        <h3 className="pricing-breakdown-title">Your Booking Summary</h3>
        <p className="pricing-breakdown-subtitle">
          Skill: <strong>{skillLabel}</strong> | Location: <strong>{locationText}</strong>
        </p>
      </div>

      <div className="urgency-selector">
        <label className="urgency-label">Urgency</label>
        <div className="urgency-options">
          <button
            type="button"
            className={`urgency-chip ${urgency === 'normal' ? 'active' : ''}`}
            onClick={() => onUrgencyChange('normal')}
          >
            Standard
          </button>
          <button
            type="button"
            className={`urgency-chip ${urgency === 'urgent' ? 'active' : ''}`}
            onClick={() => onUrgencyChange('urgent')}
          >
            Urgent (+20%)
          </button>
          <button
            type="button"
            className={`urgency-chip ${urgency === 'emergency' ? 'active' : ''}`}
            onClick={() => onUrgencyChange('emergency')}
          >
            Emergency (+35%)
          </button>
        </div>
      </div>

      {isLoading && <div className="loading-state">Calculating transparent price...</div>}

      {error && !isLoading && (
        <div className="loading-state" style={{ color: 'var(--color-status-error)' }}>
          {error}
        </div>
      )}

      {pricingData && !isLoading && (
        <div className="pricing-rows">
          <div className="pricing-row">
            <span>Base rate:</span>
            <span>₹{Number(pricingData.base_price).toFixed(2)}</span>
          </div>

          {pricingData.is_surging && Number(pricingData.surge_surplus) > 0 && (
            <div className="pricing-row surge">
              <span>
                Demand surge:
                <span className="surge-tag">HIGH DEMAND</span>
              </span>
              <span>+₹{Number(pricingData.surge_surplus).toFixed(2)}</span>
            </div>
          )}

          <hr className="pricing-divider" />

          <div className="pricing-row total">
            <span>You pay:</span>
            <span>₹{Number(pricingData.final_price).toFixed(2)}</span>
          </div>

          <div className="pricing-row worker-earns">
            <span>Worker earns:</span>
            <span>₹{Number(pricingData.worker_earns).toFixed(2)}</span>
          </div>

          <div className="pricing-row welfare-fund">
            <span>Welfare Fund:</span>
            <span>+₹{Number(pricingData.welfare_fund_contribution).toFixed(2)}</span>
          </div>
        </div>
      )}
    </div>
  );
}
