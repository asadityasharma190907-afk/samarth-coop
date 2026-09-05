import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PhotoProofCard } from './PhotoProofCard';

describe('PhotoProofCard', () => {
  it('renders placeholders when no photos are provided', () => {
    render(<PhotoProofCard />);

    expect(screen.getByText('Work Verification & Photo Proof')).toBeInTheDocument();
    expect(screen.getByText('No Proof Uploaded')).toBeInTheDocument();
    expect(screen.getByText('No before photo uploaded')).toBeInTheDocument();
    expect(screen.getByText('No after photo uploaded')).toBeInTheDocument();
  });

  it('renders before and after photos when provided', () => {
    render(
      <PhotoProofCard
        beforePhotoUrl="/uploads/before_1.jpg"
        afterPhotoUrl="/uploads/after_1.jpg"
      />,
    );

    expect(screen.getByText('Verified Proof')).toBeInTheDocument();
    const images = screen.getAllByRole('img');
    expect(images.length).toBe(2);
    expect(images[0]).toHaveAttribute('alt', 'Before work proof');
    expect(images[1]).toHaveAttribute('alt', 'After completion proof');
  });

  it('opens and closes zoom modal on photo click', () => {
    render(
      <PhotoProofCard
        beforePhotoUrl="/uploads/before_1.jpg"
        afterPhotoUrl="/uploads/after_1.jpg"
      />,
    );

    const beforeWrap = screen.getByLabelText('Zoom Before Work Photo');
    fireEvent.click(beforeWrap);

    expect(screen.getByLabelText('Close enlarged photo')).toBeInTheDocument();

    const closeBtn = screen.getByLabelText('Close enlarged photo');
    fireEvent.click(closeBtn);

    expect(screen.queryByLabelText('Close enlarged photo')).not.toBeInTheDocument();
  });
});
