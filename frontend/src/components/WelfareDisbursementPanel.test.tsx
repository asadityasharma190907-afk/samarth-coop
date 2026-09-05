import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { WelfareDisbursementPanel } from './WelfareDisbursementPanel';

vi.mock('../hooks/useWelfare', () => ({
  useWelfareSummary: () => ({
    data: {
      total_fees: 50000,
      completed_bookings: 25,
      total_disbursed: 20000,
      remaining_balance: 30000,
      category_breakdown: {
        insurance: 15000,
        tool_loan: 5000,
      },
    },
    isLoading: false,
  }),
  useWelfareDisbursements: () => ({
    data: [
      {
        id: 'disburse-1',
        amount: 15000,
        category: 'insurance',
        description: 'Group health policy premium',
        disbursed_at: '2026-09-05T12:00:00Z',
      },
      {
        id: 'disburse-2',
        amount: 5000,
        category: 'tool_loan',
        description: 'Tool kit support for Ramesh',
        disbursed_at: '2026-09-04T10:00:00Z',
      },
    ],
    isLoading: false,
  }),
}));

describe('WelfareDisbursementPanel Component', () => {
  const queryClient = new QueryClient();

  it('renders summary statistics and category breakdown correctly', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <WelfareDisbursementPanel />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/Cooperative Welfare Fund Governance/i)).toBeInTheDocument();
    expect(screen.getByText('Total Fund Collected')).toBeInTheDocument();
    expect(screen.getByText('Remaining Unspent Balance')).toBeInTheDocument();
    expect(screen.getByText('Fund Allocation Breakdown')).toBeInTheDocument();
    expect(screen.getByText('Recent Fund Disbursements')).toBeInTheDocument();
    expect(screen.getByText('Group health policy premium')).toBeInTheDocument();
  });
});
