import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import './FairnessMetricsPanel.css';

export interface WorkerOfferDistributionItem {
  worker_id: string;
  worker_name: string;
  skill: string;
  offers_count: number;
  completed_bookings_count: number;
  weekly_earnings: number;
}

export interface IncomeRangeStats {
  min_earnings: number;
  max_earnings: number;
  median_earnings: number;
  average_earnings: number;
  gap_ratio: number;
}

export interface FairnessMetricsResponse {
  samarth_gini: number;
  proximity_gini: number;
  gini_improvement_pct: number;
  income_range: IncomeRangeStats;
  meena_effect_count: number;
  meena_effect_description: string;
  offers_distribution: WorkerOfferDistributionItem[];
  total_active_workers: number;
  total_weekly_earnings: number;
}

export function FairnessMetricsPanel() {
  const { data, isLoading, error } = useQuery<FairnessMetricsResponse>({
    queryKey: ['fairnessMetrics'],
    queryFn: async () => {
      const response = await api.get('/analytics/fairness');
      return response as FairnessMetricsResponse;
    },
    refetchInterval: 10000,
  });

  if (isLoading) {
    return <div className="fairness-loading">Loading income fairness metrics...</div>;
  }

  if (error || !data) {
    return (
      <div className="fairness-error">
        Failed to load fairness metrics. Please ensure the backend is running.
      </div>
    );
  }

  const maxWeeklyEarnings = Math.max(
    ...data.offers_distribution.map((d) => d.weekly_earnings),
    1,
  );

  return (
    <div className="fairness-panel-container">
      <div className="fairness-header">
        <div className="fairness-title-group">
          <h2>Income Fairness & Gini Coefficient</h2>
          <p>
            Real-time algorithmic fairness metrics comparing cooperative dispatch vs. proximity
            dispatch
          </p>
        </div>
        <div className="fairness-live-badge">
          <span className="live-dot" />
          Live Audit Engine
        </div>
      </div>

      <div className="gini-comparison-card">
        <div className="gini-header">
          <h3>Gini Coefficient Benchmark</h3>
          <span className="gini-improvement-pill">
            +{data.gini_improvement_pct}% Income Equality Improvement
          </span>
        </div>

        <div className="gini-gauges-grid">
          <div className="gini-gauge-box samarth">
            <span className="gauge-tag">Samarth Cooperative Dispatch</span>
            <span className="gauge-value">{data.samarth_gini.toFixed(2)}</span>
            <div className="gauge-bar-track">
              <div
                className="gauge-bar-fill samarth"
                style={{ width: `${Math.min(data.samarth_gini * 100, 100)}%` }}
              />
            </div>
            <span className="gauge-caption">Equitable Distribution across active pool</span>
          </div>

          <div className="gini-gauge-box proximity">
            <span className="gauge-tag">Standard Proximity Dispatch (VC Baseline)</span>
            <span className="gauge-value">{data.proximity_gini.toFixed(2)}</span>
            <div className="gauge-bar-track">
              <div
                className="gauge-bar-fill proximity"
                style={{ width: `${Math.min(data.proximity_gini * 100, 100)}%` }}
              />
            </div>
            <span className="gauge-caption">High Concentration of orders to nearest worker</span>
          </div>
        </div>

        <p className="gini-explanation">
          Note: Gini index ranges from 0.0 (perfect equality) to 1.0 (perfect inequality). Samarth
          weekly earnings penalty actively redistributes dispatch priority to maintain a low Gini
          index.
        </p>
      </div>

      <div className="meena-effect-banner">
        <div className="meena-counter-circle">
          <span className="counter-num">{data.meena_effect_count}</span>
          <span className="counter-label">Interventions</span>
        </div>
        <div className="meena-content">
          <h4>The "Meena Effect" Counter</h4>
          <p>
            {data.meena_effect_description ||
              'Times fairness dispatch prioritized a low-earning worker over a closer or higher-rated peer.'}
          </p>
        </div>
      </div>

      <div className="income-stats-grid">
        <div className="income-stat-card">
          <span className="stat-label">Min Weekly Earnings</span>
          <span className="stat-value">₹{data.income_range.min_earnings.toLocaleString()}</span>
          <span className="stat-subtext">Cold-start / New workers</span>
        </div>

        <div className="income-stat-card">
          <span className="stat-label">Max Weekly Earnings</span>
          <span className="stat-value">₹{data.income_range.max_earnings.toLocaleString()}</span>
          <span className="stat-subtext">Ceiling before priority shift</span>
        </div>

        <div className="income-stat-card">
          <span className="stat-label">Median Weekly Income</span>
          <span className="stat-value">₹{data.income_range.median_earnings.toLocaleString()}</span>
          <span className="stat-subtext">Midpoint across workers</span>
        </div>

        <div className="income-stat-card">
          <span className="stat-label">Top-to-Bottom Ratio</span>
          <span className="stat-value">{data.income_range.gap_ratio}x</span>
          <span className="stat-subtext">Spread ratio (Max / Min)</span>
        </div>
      </div>

      <div className="offers-distribution-card">
        <div className="offers-header">
          <h3>Worker Dispatch Distribution</h3>
          <p>Weekly jobs and earnings distribution across all registered cooperative members</p>
        </div>

        <div className="distribution-table-container">
          <table className="distribution-table">
            <thead>
              <tr>
                <th>Worker</th>
                <th>Offers Received</th>
                <th>Completed Jobs</th>
                <th>Weekly Earnings</th>
                <th>Income Share</th>
              </tr>
            </thead>
            <tbody>
              {data.offers_distribution.map((item) => {
                const sharePct = Math.round((item.weekly_earnings / maxWeeklyEarnings) * 100);
                return (
                  <tr key={item.worker_id}>
                    <td className="worker-name-cell">
                      {item.worker_name}
                      <span className="skill-tag">{item.skill}</span>
                    </td>
                    <td>{item.offers_count}</td>
                    <td>{item.completed_bookings_count}</td>
                    <td>
                      <strong>₹{item.weekly_earnings.toLocaleString()}</strong>
                    </td>
                    <td className="distribution-bar-cell">
                      <div className="progress-track" title={`${sharePct}% of max`}>
                        <div
                          className="progress-fill"
                          style={{ width: `${Math.max(sharePct, 4)}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
