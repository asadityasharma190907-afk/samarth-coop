import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { OfferCard } from './OfferCard';
import { WorkerOfferDetail } from '../hooks/useOffers';

vi.mock('../lib/api', () => ({
  api: {
    put: vi.fn(),
  },
}));

describe('OfferCard Component - Citizen Trust Indicator (Story 15.3)', () => {
  const createQueryClient = () =>
    new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

  const baseOffer: WorkerOfferDetail = {
    id: 'offer-123',
    booking_id: 'booking-456',
    worker_id: 'worker-789',
    rank_at_offer: 1,
    dispatch_score: 12000,
    status: 'offered',
    expires_at: new Date(Date.now() + 60000).toISOString(),
    created_at: new Date().toISOString(),
    job_price: 500,
    skill: 'Electrician',
    lat: 26.9124,
    lng: 75.7873,
    distance_km: 2.1,
    citizen_trust_score: 100,
    citizen_trust_level: null,
  };

  it('renders offer details correctly', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <OfferCard offer={baseOffer} />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Electrician')).toBeInTheDocument();
    expect(screen.getByText('₹500.00')).toBeInTheDocument();
    expect(screen.getByText('2.1 km away')).toBeInTheDocument();
  });

  it('does NOT show trust warning when citizen trust score is >= 80', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <OfferCard offer={{ ...baseOffer, citizen_trust_score: 100, citizen_trust_level: null }} />
      </QueryClientProvider>,
    );

    expect(screen.queryByTestId('citizen-trust-warning')).not.toBeInTheDocument();
    expect(screen.queryByText(/cancellation/i)).not.toBeInTheDocument();
  });

  it('shows warning indicator when citizen trust score is between 60 and 79', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <OfferCard
          offer={{
            ...baseOffer,
            citizen_trust_score: 72,
            citizen_trust_level: 'high_cancellation',
          }}
        />
      </QueryClientProvider>,
    );

    const warning = screen.getByTestId('citizen-trust-warning');
    expect(warning).toBeInTheDocument();
    expect(screen.getByText('High cancellation history')).toBeInTheDocument();
    expect(screen.getByText('Trust 72/100')).toBeInTheDocument();
  });

  it('shows caution indicator when citizen trust score is between 40 and 59', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <OfferCard
          offer={{
            ...baseOffer,
            citizen_trust_score: 55,
            citizen_trust_level: 'confirm_required',
          }}
        />
      </QueryClientProvider>,
    );

    const warning = screen.getByTestId('citizen-trust-warning');
    expect(warning).toBeInTheDocument();
    expect(screen.getByText('Confirm before accepting')).toBeInTheDocument();
    expect(screen.getByText('Trust 55/100')).toBeInTheDocument();
  });

  it('shows restricted indicator when citizen trust score is below 40', () => {
    render(
      <QueryClientProvider client={createQueryClient()}>
        <OfferCard
          offer={{
            ...baseOffer,
            citizen_trust_score: 25,
            citizen_trust_level: 'restricted',
          }}
        />
      </QueryClientProvider>,
    );

    const warning = screen.getByTestId('citizen-trust-warning');
    expect(warning).toBeInTheDocument();
    expect(screen.getByText('Restricted citizen')).toBeInTheDocument();
    expect(screen.getByText('Trust 25/100')).toBeInTheDocument();
  });
});
