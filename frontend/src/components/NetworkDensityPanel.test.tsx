import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { NetworkDensityPanel } from './NetworkDensityPanel';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

describe('NetworkDensityPanel', () => {
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
        <NetworkDensityPanel />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId('density-loading')).toBeInTheDocument();
  });

  it('renders network density panel with skill metrics and waves', async () => {
    vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url === '/federation/bookings') {
        return [
          { id: '1', skill: 'electrician', status: 'pending' },
          { id: '2', skill: 'electrician', status: 'assigned' },
          { id: '3', skill: 'plumber', status: 'completed' },
        ];
      }
      if (url.includes('skill=electrician')) {
        return [
          { worker_id: 'w1', name: 'Suresh Kumar', wave_used: 1, effective_radius_km: 3.0 },
          { worker_id: 'w2', name: 'Priya Gupta', wave_used: 1, effective_radius_km: 3.0 },
        ];
      }
      if (url.includes('skill=plumber')) {
        return [
          { worker_id: 'w3', name: 'Ramesh Singh', wave_used: 1, effective_radius_km: 3.0 },
          { worker_id: 'w4', name: 'Mohan Lal', wave_used: 1, effective_radius_km: 3.0 },
          { worker_id: 'w5', name: 'Dinesh', wave_used: 1, effective_radius_km: 3.0 },
          { worker_id: 'w6', name: 'Vikas', wave_used: 1, effective_radius_km: 3.0 },
        ];
      }
      if (url.includes('skill=carpenter')) {
        return [
          { worker_id: 'w7', name: 'Sunil', wave_used: 2, effective_radius_km: 5.0 },
        ];
      }
      if (url.includes('skill=ac_mechanic')) {
        return [
          { worker_id: 'w8', name: 'Arun', wave_used: 3, effective_radius_km: 8.0 },
        ];
      }
      return [];
    });

    render(
      <QueryClientProvider client={createQueryClient()}>
        <NetworkDensityPanel />
      </QueryClientProvider>,
    );

    // Verify header and title
    expect(await screen.findByText(/Network Density & Dispatch Elasticity \(Live\)/i)).toBeInTheDocument();
    expect(screen.getByText('Live Governance Signals')).toBeInTheDocument();

    // Verify skills rendered
    expect(screen.getByText('Electrician')).toBeInTheDocument();
    expect(screen.getByText('Plumber')).toBeInTheDocument();
    expect(screen.getByText('Carpenter')).toBeInTheDocument();
    expect(screen.getByText('AC Mechanic')).toBeInTheDocument();

    // Verify KPI highlights
    expect(screen.getByText('Network D/S Average')).toBeInTheDocument();
    expect(screen.getByText('Active Expansion Wave')).toBeInTheDocument();

    // Verify wave badges & status pills
    expect(screen.getAllByText('W1').length).toBeGreaterThan(0);
    expect(screen.getByText('Ministry / NCCT Evaluator Note: Dynamic Radius Elasticity')).toBeInTheDocument();
  });

  it('renders error message when API fails', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('Network failure'));

    render(
      <QueryClientProvider client={createQueryClient()}>
        <NetworkDensityPanel />
      </QueryClientProvider>,
    );

    expect(await screen.findByTestId('density-error')).toBeInTheDocument();
  });
});
