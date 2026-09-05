import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { GenderPreferenceSelector } from './GenderPreferenceSelector';

describe('GenderPreferenceSelector', () => {
  it('renders all 3 gender preference options', () => {
    render(<GenderPreferenceSelector selected="any" onChange={() => {}} />);

    expect(screen.getByText('Any Worker')).toBeInTheDocument();
    expect(screen.getByText('Female Preferred')).toBeInTheDocument();
    expect(screen.getByText('Male Preferred')).toBeInTheDocument();
  });

  it('marks the currently selected option as active', () => {
    const { rerender } = render(<GenderPreferenceSelector selected="female" onChange={() => {}} />);

    const femaleChip = screen.getByTestId('gender-chip-female');
    const maleChip = screen.getByTestId('gender-chip-male');
    const anyChip = screen.getByTestId('gender-chip-any');

    expect(femaleChip).toHaveClass('selected');
    expect(femaleChip).toHaveAttribute('aria-pressed', 'true');
    expect(maleChip).not.toHaveClass('selected');
    expect(anyChip).not.toHaveClass('selected');

    rerender(<GenderPreferenceSelector selected="male" onChange={() => {}} />);
    expect(screen.getByTestId('gender-chip-male')).toHaveClass('selected');
  });

  it('calls onChange callback when clicking an option', () => {
    const handleChange = vi.fn();
    render(<GenderPreferenceSelector selected="any" onChange={handleChange} />);

    const femaleChip = screen.getByTestId('gender-chip-female');
    fireEvent.click(femaleChip);

    expect(handleChange).toHaveBeenCalledWith('female');
  });

  it('renders informational context banner', () => {
    render(<GenderPreferenceSelector selected="any" onChange={() => {}} />);

    expect(
      screen.getByText(/Female workers available for cleaning, caregiving & domestic help tasks/i),
    ).toBeInTheDocument();
  });
});
