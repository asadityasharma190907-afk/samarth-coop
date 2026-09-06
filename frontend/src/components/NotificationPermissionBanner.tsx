import React, { useState } from 'react';
import { usePushSubscription } from '../hooks/usePushSubscription';
import './NotificationPermissionBanner.css';

export function NotificationPermissionBanner() {
  const { permission, isSubscribing, isSubscribed, subscribeToPush } = usePushSubscription();
  const [dismissed, setDismissed] = useState(false);

  if (dismissed || isSubscribed || permission === 'granted' || permission === 'denied') {
    return null;
  }

  return (
    <div className="notification-permission-banner" data-testid="push-permission-banner">
      <div className="notification-banner-content">
        <div className="notification-banner-icon">
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
        </div>
        <div>
          <div className="notification-banner-title">Enable Job Offer Alerts</div>
          <div className="notification-banner-desc">
            Get instant browser alerts when new job offers match your skill — even when offline or
            tab closed.
          </div>
        </div>
      </div>
      <div className="notification-banner-actions">
        <button
          className="btn-enable-push"
          onClick={() => subscribeToPush()}
          disabled={isSubscribing}
          data-testid="enable-push-btn"
        >
          {isSubscribing ? 'Enabling...' : 'Enable Notifications'}
        </button>
        <button
          className="btn-dismiss-banner"
          onClick={() => setDismissed(true)}
          aria-label="Dismiss banner"
          data-testid="dismiss-push-banner-btn"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
