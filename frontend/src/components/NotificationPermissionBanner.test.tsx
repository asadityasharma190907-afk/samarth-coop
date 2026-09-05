import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NotificationPermissionBanner } from './NotificationPermissionBanner';

vi.mock('../hooks/usePushSubscription', () => ({
  usePushSubscription: () => ({
    permission: 'default',
    isSubscribing: false,
    isSubscribed: false,
    error: null,
    subscribeToPush: vi.fn(),
  }),
}));

describe('NotificationPermissionBanner Component', () => {
  it('renders permission banner when permission is default', () => {
    render(<NotificationPermissionBanner />);

    expect(screen.getByTestId('push-permission-banner')).toBeInTheDocument();
    expect(screen.getByText('Enable Job Offer Alerts')).toBeInTheDocument();
    expect(screen.getByTestId('enable-push-btn')).toBeInTheDocument();
  });

  it('allows user to dismiss the banner', () => {
    render(<NotificationPermissionBanner />);

    const dismissBtn = screen.getByTestId('dismiss-push-banner-btn');
    fireEvent.click(dismissBtn);

    expect(screen.queryByTestId('push-permission-banner')).not.toBeInTheDocument();
  });
});
