import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { PricingBreakdownCard } from './PricingBreakdownCard';

const mockPricingData = {
  skill: 'electrician',
  base_price: 500,
  final_price: 650,
  surge_surplus: 150,
  is_surging: true,
  surge_reason: 'High demand in your area',
  urgency_multiplier: 1.0,
  worker_earns: 580,
  welfare_fund_contribution: 32.5,
  platform_fee: 17.5,
};

describe('PricingBreakdownCard', () => {
  it('renders correctly with price breakdown and surge line when surging', () => {
    render(
      <PricingBreakdownCard
        skillLabel="Electrician"
        locationText="26.9124, 75.7873"
        urgency="normal"
        onUrgencyChange={vi.fn()}
        pricingData={mockPricingData}
        isLoading={false}
      />,
    );

    expect(screen.getByText('Your Booking Summary')).toBeInTheDocument();
    expect(screen.getByText('Electrician')).toBeInTheDocument();
    expect(screen.getByText('₹500.00')).toBeInTheDocument();
    expect(screen.getByText('+₹150.00')).toBeInTheDocument();
    expect(screen.getByText('HIGH DEMAND')).toBeInTheDocument();
    expect(screen.getByText('₹650.00')).toBeInTheDocument();
    expect(screen.getByText('₹580.00')).toBeInTheDocument();
    expect(screen.getByText('+₹32.50')).toBeInTheDocument();
  });

  it('hides surge line when not surging', () => {
    const nonSurgingData = {
      ...mockPricingData,
      final_price: 500,
      surge_surplus: 0,
      is_surging: false,
    };

    render(
      <PricingBreakdownCard
        skillLabel="Electrician"
        locationText="26.9124, 75.7873"
        urgency="normal"
        onUrgencyChange={vi.fn()}
        pricingData={nonSurgingData}
        isLoading={false}
      />,
    );

    expect(screen.queryByText('HIGH DEMAND')).not.toBeInTheDocument();
    expect(screen.queryByText('Demand surge:')).not.toBeInTheDocument();
    expect(screen.getAllByText('₹500.00').length).toBe(2);
  });

  it('triggers onUrgencyChange when urgency buttons are clicked', () => {
    const handleUrgencyChange = vi.fn();

    render(
      <PricingBreakdownCard
        skillLabel="Electrician"
        locationText="26.9124, 75.7873"
        urgency="normal"
        onUrgencyChange={handleUrgencyChange}
        pricingData={mockPricingData}
        isLoading={false}
      />,
    );

    fireEvent.click(screen.getByText('Urgent (+20%)'));
    expect(handleUrgencyChange).toHaveBeenCalledWith('urgent');

    fireEvent.click(screen.getByText('Emergency (+35%)'));
    expect(handleUrgencyChange).toHaveBeenCalledWith('emergency');
  });

  it('renders loading state when isLoading is true', () => {
    render(
      <PricingBreakdownCard
        skillLabel="Electrician"
        locationText="26.9124, 75.7873"
        urgency="normal"
        onUrgencyChange={vi.fn()}
        isLoading={true}
      />,
    );

    expect(screen.getByText('Calculating transparent price...')).toBeInTheDocument();
  });
});
