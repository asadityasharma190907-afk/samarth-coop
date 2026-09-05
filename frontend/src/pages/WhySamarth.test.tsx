import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { WhySamarth } from './WhySamarth';

describe('WhySamarth Page', () => {
  const renderWithRouter = () => {
    return render(
      <BrowserRouter>
        <WhySamarth />
      </BrowserRouter>,
    );
  };

  it('renders the main headline and subtitle', () => {
    renderWithRouter();
    expect(screen.getByText('The platform Urban Company cannot build.')).toBeInTheDocument();
    expect(screen.getByText(/SIH Problem #26089/i)).toBeInTheDocument();
  });

  it('renders all 8 comparison dimensions in the table', () => {
    renderWithRouter();
    const dimensions = [
      'Platform cut',
      'Price transparency',
      'Lowest earner gets next job',
      'Worker owns platform',
      'Dispute proof (photo)',
      'Welfare fund',
      'Government backing',
      'Dispatch audit trail',
    ];

    dimensions.forEach((dim) => {
      expect(screen.getAllByText(dim)[0]).toBeInTheDocument();
    });

    expect(screen.getAllByText('5%')[0]).toBeInTheDocument();
    expect(screen.getByText('25-30%')).toBeInTheDocument();
    expect(screen.getByText('0%*')).toBeInTheDocument();
    expect(screen.getByText('Ministry of Cooperation')).toBeInTheDocument();
  });

  it('renders the 3 narrative pillar sections and formula', () => {
    renderWithRouter();
    expect(screen.getByText('Our Algorithm is Fairness')).toBeInTheDocument();
    expect(screen.getByText('The Cooperative Difference')).toBeInTheDocument();
    expect(screen.getByText('Built for Bharat')).toBeInTheDocument();

    expect(screen.getByText(/Score = \(5000 − WeeklyEarnings\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Meena Verma/i)).toBeInTheDocument();
    expect(screen.getByText(/Suresh Kumar/i)).toBeInTheDocument();
  });

  it('renders navigation links and action buttons', () => {
    renderWithRouter();
    expect(screen.getByRole('button', { name: /Back to Login/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Join Cooperative/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Create an Account/i })).toBeInTheDocument();
  });
});
