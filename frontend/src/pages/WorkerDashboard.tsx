import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock } from 'lucide-react';
import { BottomTabNav } from '../components/BottomTabNav';
import { useProfile } from '../hooks/useProfile';

const TABS = [
  { id: 'home', label: 'Home', icon: '🏠', path: '/worker/dashboard' },
  { id: 'offers', label: 'Offers', icon: '📋', path: '/worker/offers' },
  { id: 'wallet', label: 'Wallet', icon: '💳', path: '/worker/wallet' },
  { id: 'profile', label: 'Profile', icon: '👤', path: '/worker/profile' },
];

export function WorkerDashboard() {
  const navigate = useNavigate();
  const { data: profile } = useProfile();

  const handleLogout = () => {
    localStorage.removeItem('samarth_token');
    navigate('/login');
  };

  return (
    <div
      style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--color-surface-bg)' }}
    >
      {/* Desktop Sidebar (hidden on mobile) */}
      <div
        className="desktop-sidebar"
        style={{
          width: '240px',
          backgroundColor: 'var(--color-surface-card)',
          borderRight: '1px solid var(--color-border-default)',
          padding: 'var(--spacing-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-md)',
        }}
      >
        <style>{`
          @media (max-width: 1023px) {
            .desktop-sidebar {
              display: none !important;
            }
          }
        `}</style>

        <h2 style={{ fontSize: 'var(--font-size-h3)', color: 'var(--color-brand-primary)' }}>
          Samarth Pro
        </h2>

        <nav
          style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', flex: 1 }}
        >
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => navigate(tab.path)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                padding: '12px',
                background: tab.id === 'home' ? 'var(--color-surface-overlay)' : 'none',
                color:
                  tab.id === 'home' ? 'var(--color-brand-primary)' : 'var(--color-text-secondary)',
                border: 'none',
                borderRadius: 'var(--rounded-md)',
                cursor: 'pointer',
                textAlign: 'left',
                fontWeight: 'var(--font-weight-medium)',
                fontSize: 'var(--font-size-body)',
              }}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>

        <button
          onClick={handleLogout}
          style={{
            padding: '12px',
            backgroundColor: 'transparent',
            color: 'var(--color-text-secondary)',
            border: '1px solid var(--color-border-default)',
            borderRadius: 'var(--rounded-md)',
            cursor: 'pointer',
            textAlign: 'center',
          }}
        >
          Log out
        </button>
      </div>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: 'var(--spacing-lg)', paddingBottom: '80px' }}>
        {profile?.verification_status === 'pending' && (
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 'var(--spacing-sm)',
              padding: 'var(--spacing-md)',
              backgroundColor: 'rgba(217, 119, 6, 0.1)',
              border: '1px solid var(--color-status-warning)',
              borderRadius: 'var(--rounded-md)',
              color: 'var(--color-status-warning)',
              marginBottom: 'var(--spacing-xl)',
            }}
          >
            <Clock size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ fontSize: 'var(--font-size-body)', lineHeight: 'var(--line-height-body)' }}>
              Your profile is currently under cooperative review. You will start receiving job offers once verified by the society administrator.
            </div>
          </div>
        )}

        <h1>Worker Dashboard</h1>
        <p>Welcome! You are ready to receive job offers.</p>

        {/* Mobile logout button since sidebar is hidden */}
        <div className="mobile-logout" style={{ marginTop: 'var(--spacing-xl)' }}>
          <style>{`
            @media (min-width: 1024px) {
              .mobile-logout {
                display: none !important;
              }
            }
          `}</style>
          <button
            onClick={handleLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: 'var(--color-surface-card)',
              color: 'var(--color-status-error)',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              cursor: 'pointer',
            }}
          >
            Log out
          </button>
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
      <BottomTabNav />
    </div>
  );
}
