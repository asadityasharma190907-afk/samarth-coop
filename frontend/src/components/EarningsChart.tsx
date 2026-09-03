import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import './EarningsChart.css';

interface EarningsBucketItem {
  range_label: string;
  min_val: number;
  max_val: number | null;
  worker_count: number;
}

interface EarningsDistributionResponse {
  currency: string;
  total_workers: number;
  buckets: EarningsBucketItem[];
}

export function EarningsChart() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['earningsDistribution'],
    queryFn: async () => {
      const response = await api.get('/federation/earnings-distribution');
      return response as EarningsDistributionResponse;
    },
    refetchInterval: 10000,
  });

  if (isLoading) {
    return <div className="loading-state">Loading earnings distribution...</div>;
  }

  if (error || !data) {
    return <div className="error-state">Failed to load earnings distribution.</div>;
  }

  const maxCount = Math.max(...data.buckets.map((b) => b.worker_count));
  const effectiveMax = maxCount > 0 ? maxCount : 1;

  return (
    <div className="earnings-chart-container">
      <div className="chart-header">
        <h3>Weekly Earnings Distribution</h3>
        <span className="total-workers-badge">{data.total_workers} Active Workers</span>
      </div>

      <div className="chart-body">
        <div className="bars-container">
          {data.buckets.map((bucket, index) => {
            const heightPct = (bucket.worker_count / effectiveMax) * 100;
            return (
              <div key={index} className="bar-wrapper">
                <div
                  className="bar"
                  style={{ height: `${heightPct}%` }}
                  title={`${bucket.worker_count} worker${bucket.worker_count !== 1 ? 's' : ''}`}
                >
                  <span className="bar-tooltip">{bucket.worker_count}</span>
                </div>
                <div className="bar-label">{bucket.range_label}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
