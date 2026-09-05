import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { FairnessMetricsPanel } from './FairnessMetricsPanel';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

describe('FairnessMetricsPanel', () => {
  const createQueryClient = () =>
    new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

  it('renders loading state initially', () => {
    vi.mocked(api.get).mockImplementation(() => new Promise(() => {}));

    render(
      <QueryClientProvider client={createQueryClient()}>
        <FairnessMetricsPanel />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/Loading income fairness metrics.../i)).toBeInTheDocument();
  });

  it('renders fairness metrics and comparison when data loads', async () => {
    const mockData = {
      samarth_gini: 0.14,
      proximity_gini: 0.42,
      gini_improvement_pct: 66.7,
      income_range: {
        min_earnings: 0,
        max_earnings: 4500,
        median_earnings: 1100,
        average_earnings: 1675,
        gap_ratio: 22.5,
      },
      meena_effect_count: 3,
      meena_effect_description: 'Times fairness dispatch prioritized low earners.',
      offers_distribution: [
        {
          worker_id: '1',
          worker_name: 'Suresh Kumar',
          skill: 'electrician',
          offers_count: 3,
          completed_bookings_count: 1,
          weekly_earnings: 200,
        },
        {
          worker_id: '2',
          worker_name: 'Priya Gupta',
          skill: 'electrician',
          offers_count: 2,
          completed_bookings_count: 0,
          weekly_earnings: 0,
        },
        {
          worker_id: '3',
          worker_name: 'Anil Yadav',
          skill: 'electrician',
          offers_count: 4,
          completed_bookings_count: 1,
          weekly_earnings: 2000,
        },
        {
          worker_id: '4',
          worker_name: 'Meena Verma',
          skill: 'electrician',
          offers_count: 1,
          completed_bookings_count: 1,
          weekly_earnings: 4500,
        },
      ],
      total_active_workers: 4,
      total_weekly_earnings: 6700,
    };

    vi.mocked(api.get).mockResolvedValue(mockData);

    render(
      <QueryClientProvider client={createQueryClient()}>
        <FairnessMetricsPanel />
      </QueryClientProvider>,
    );

    expect(await screen.findByText('Income Fairness & Gini Coefficient')).toBeInTheDocument();
    expect(screen.getByText('+66.7% Income Equality Improvement')).toBeInTheDocument();

    expect(screen.getByText('Samarth Cooperative Dispatch')).toBeInTheDocument();
    expect(screen.getByText('Standard Proximity Dispatch (VC Baseline)')).toBeInTheDocument();
    expect(screen.getAllByText('0.14')[0]).toBeInTheDocument();
    expect(screen.getAllByText('0.42')[0]).toBeInTheDocument();

    expect(screen.getByText('The "Meena Effect" Counter')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();

    expect(screen.getByText('Min Weekly Earnings')).toBeInTheDocument();
    expect(screen.getByText('Max Weekly Earnings')).toBeInTheDocument();
    expect(screen.getByText('Median Weekly Income')).toBeInTheDocument();
    expect(screen.getByText('Top-to-Bottom Ratio')).toBeInTheDocument();
    expect(screen.getByText('22.5x')).toBeInTheDocument();

    expect(screen.getByText('Suresh Kumar')).toBeInTheDocument();
    expect(screen.getByText('Priya Gupta')).toBeInTheDocument();
    expect(screen.getByText('Anil Yadav')).toBeInTheDocument();
    expect(screen.getByText('Meena Verma')).toBeInTheDocument();
  });

  it('renders error state on API failure', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('Network error'));

    render(
      <QueryClientProvider client={createQueryClient()}>
        <FairnessMetricsPanel />
      </QueryClientProvider>,
    );

    expect(await screen.findByText(/Failed to load fairness metrics/i)).toBeInTheDocument();
  });
});
