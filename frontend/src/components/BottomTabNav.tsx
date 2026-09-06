import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useLanguage } from '../hooks/useLanguage';

const TABS = [
  { id: 'home', label: 'Home', icon: '🏠', path: '/worker/dashboard' },
  { id: 'offers', label: 'Offers', icon: '📋', path: '/worker/offers' },
  { id: 'wallet', label: 'Wallet', icon: '💳', path: '/worker/wallet' },
  { id: 'profile', label: 'Profile', icon: '👤', path: '/worker/profile' },
];

export function BottomTabNav() {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();

  return (
    <div
      className="bottom-tab-nav"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: 'var(--color-surface-card)',
        borderTop: '1px solid var(--color-border-default)',
        display: 'flex',
        justifyContent: 'space-around',
        padding: 'var(--spacing-sm) 0',
        boxShadow: '0 -2px 10px rgba(0,0,0,0.05)',
        zIndex: 50,
      }}
    >
      <style>{`
        @media (min-width: 1024px) {
          .bottom-tab-nav {
            display: none !important;
          }
        }
      `}</style>

      {TABS.map((tab) => {
        const isActive =
          location.pathname === tab.path ||
          (tab.id === 'home' && location.pathname === '/worker/dashboard');

        return (
          <button
            key={tab.id}
            onClick={() => navigate(tab.path)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              background: 'none',
              border: 'none',
              color: isActive ? 'var(--color-brand-primary)' : 'var(--color-text-muted)',
              cursor: 'pointer',
            }}
          >
            <span style={{ fontSize: '1.25rem' }}>{tab.icon}</span>
            <span
              style={{
                fontSize: 'var(--font-size-caption)',
                fontWeight: isActive ? 'var(--font-weight-semibold)' : 'var(--font-weight-medium)',
              }}
            >
              {tab.id !== 'home' ? t(`nav.${tab.id}`) : tab.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
