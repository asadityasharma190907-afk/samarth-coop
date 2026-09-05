import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PhotoProofUpload } from './PhotoProofUpload';

describe('PhotoProofUpload', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders upload prompt for before photo when no photo is uploaded', () => {
    render(<PhotoProofUpload bookingId="booking-123" photoType="before" />);

    expect(screen.getByText('Before Work Photo')).toBeInTheDocument();
    expect(screen.getByText('Upload or Capture Photo')).toBeInTheDocument();
  });

  it('renders uploaded preview when photoUrl is present', () => {
    render(
      <PhotoProofUpload
        bookingId="booking-123"
        photoType="after"
        currentPhotoUrl="/uploads/after_123.jpg"
      />,
    );

    expect(screen.getByText('After Work Photo')).toBeInTheDocument();
    expect(screen.getByText('Uploaded')).toBeInTheDocument();
    expect(screen.getByRole('img')).toBeInTheDocument();
    expect(screen.getByText('Retake Photo')).toBeInTheDocument();
  });

  it('handles successful photo upload', async () => {
    const handleUploaded = vi.fn();
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        photo_url: '/uploads/before_uploaded.jpg',
        before_photo_url: '/uploads/before_uploaded.jpg',
      }),
    } as any);

    render(
      <PhotoProofUpload bookingId="booking-123" photoType="before" onUploaded={handleUploaded} />,
    );

    const fileInput = screen.getByTestId('file-input-before');
    const file = new File(['fake image data'], 'site.png', { type: 'image/png' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(handleUploaded).toHaveBeenCalledWith('/uploads/before_uploaded.jpg');
    });

    expect(screen.getByText('Uploaded')).toBeInTheDocument();
  });

  it('shows error if file size exceeds 5MB', () => {
    render(<PhotoProofUpload bookingId="booking-123" photoType="before" />);

    const fileInput = screen.getByTestId('file-input-before');
    // Create large dummy file > 5MB
    const bigFile = new File([''], 'huge.png', { type: 'image/png' });
    Object.defineProperty(bigFile, 'size', { value: 6 * 1024 * 1024 });

    fireEvent.change(fileInput, { target: { files: [bigFile] } });

    expect(screen.getByText('File size must be less than 5MB')).toBeInTheDocument();
  });
});
