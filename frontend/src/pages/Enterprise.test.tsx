import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Enterprise } from './Enterprise';
import * as apiModule from '../lib/api';

describe('Enterprise B2G Booking Page', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <Enterprise />
      </QueryClientProvider>,
    );

  it('renders enterprise header and initial form correctly', () => {
    renderComponent();

    expect(
      screen.getByRole('heading', { level: 1, name: /enterprise \/ b2g booking/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/samarth cooperative services/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/institution name/i)).toBeInTheDocument();
    expect(screen.getByText(/calculate estimate/i)).toBeInTheDocument();
    expect(screen.getByText(/add another service/i)).toBeInTheDocument();
  });

  it('allows adding and removing service rows', () => {
    renderComponent();

    expect(screen.getByTestId('service-row-0')).toBeInTheDocument();
    expect(screen.queryByTestId('service-row-1')).not.toBeInTheDocument();

    // Add service row
    const addButton = screen.getByRole('button', { name: /add another service/i });
    fireEvent.click(addButton);

    expect(screen.getByTestId('service-row-1')).toBeInTheDocument();

    // Remove the added row
    const removeButtons = screen.getAllByRole('button', { name: /remove service/i });
    fireEvent.click(removeButtons[1]);

    expect(screen.queryByTestId('service-row-1')).not.toBeInTheDocument();
  });

  it('calculates estimate and displays result card upon form submission', async () => {
    const mockApiResponse = {
      contract_id: '11111111-2222-3333-4444-555555555555',
      institution: 'District Collectorate, Jaipur',
      total_bookings: 2,
      estimated_monthly_cost: '44000.00',
      cooperative_workers_needed: 2,
      welfare_fund_contribution: '2200.00',
      line_items: [
        {
          skill: 'electrician',
          quantity: 2,
          schedule: 'daily',
          months: 1,
          base_rate: '500.00',
          schedule_multiplier: 22,
          monthly_cost: '22000.00',
          total_cost: '22000.00',
          workers_needed: 2,
        },
      ],
    };

    vi.spyOn(apiModule.api, 'post').mockResolvedValueOnce(mockApiResponse);

    renderComponent();

    const institutionInput = screen.getByLabelText(/institution name/i);
    fireEvent.change(institutionInput, {
      target: { value: 'District Collectorate, Jaipur' },
    });

    const submitBtn = screen.getByRole('button', { name: /calculate estimate/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByTestId('result-card')).toBeInTheDocument();
    });

    expect(screen.getByText(/contract estimate summary/i)).toBeInTheDocument();
    expect(screen.getByText(/district collectorate, jaipur/i)).toBeInTheDocument();
    expect(screen.getByText(/total bookings \/ month/i)).toBeInTheDocument();
    expect(screen.getByText(/cooperative workers needed/i)).toBeInTheDocument();
    expect(screen.getByText(/welfare fund contribution/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /download contract pdf/i })).toBeInTheDocument();
  });

  it('triggers window.print when download contract PDF is clicked', async () => {
    const printSpy = vi.spyOn(window, 'print').mockImplementation(() => {});
    const mockApiResponse = {
      contract_id: '11111111-2222-3333-4444-555555555555',
      institution: 'District Collectorate, Jaipur',
      total_bookings: 1,
      estimated_monthly_cost: '11000.00',
      cooperative_workers_needed: 1,
      welfare_fund_contribution: '550.00',
      line_items: [],
    };

    vi.spyOn(apiModule.api, 'post').mockResolvedValueOnce(mockApiResponse);

    renderComponent();

    fireEvent.change(screen.getByLabelText(/institution name/i), {
      target: { value: 'District Collectorate, Jaipur' },
    });
    fireEvent.click(screen.getByRole('button', { name: /calculate estimate/i }));

    await waitFor(() => {
      expect(screen.getByTestId('result-card')).toBeInTheDocument();
    });

    const printBtn = screen.getByRole('button', { name: /download contract pdf/i });
    fireEvent.click(printBtn);

    expect(printSpy).toHaveBeenCalledTimes(1);
    printSpy.mockRestore();
  });
});
