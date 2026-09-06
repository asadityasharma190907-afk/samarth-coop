import React from 'react';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { BottomTabNav } from '../components/BottomTabNav';
import { useLanguage } from '../hooks/useLanguage';
import { LanguageToggle } from '../components/LanguageToggle';

const TABS = [
  { id: 'home', label: 'Home', icon: '🏠', path: '/worker/dashboard' },
  { id: 'offers', label: 'Offers', icon: '📋', path: '/worker/offers' },
  { id: 'wallet', label: 'Wallet', icon: '💳', path: '/worker/wallet' },
  { id: 'profile', label: 'Profile', icon: '👤', path: '/worker/profile' },
];

export function WorkerDashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();

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

        <div style={{ marginBottom: 'var(--spacing-md)' }}>
          <LanguageToggle />
        </div>

        <nav
          style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', flex: 1 }}
        >
          {TABS.map((tab) => {
            const isActive =
              location.pathname === tab.path ||
              (tab.id === 'home' && location.pathname === '/worker');

            return (
              <button
                key={tab.id}
                onClick={() => navigate(tab.path)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-sm)',
                  padding: '12px',
                  background: isActive ? 'var(--color-surface-overlay)' : 'none',
                  color: isActive ? 'var(--color-brand-primary)' : 'var(--color-text-secondary)',
                  border: 'none',
                  borderRadius: 'var(--rounded-md)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontWeight: 'var(--font-weight-medium)',
                  fontSize: 'var(--font-size-body)',
                }}
              >
                <span>{tab.icon}</span>
                {tab.id !== 'home' ? t(`nav.${tab.id}`) : tab.label}
              </button>
            );
          })}
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
      <main
        style={{ flex: 1, padding: 'var(--spacing-lg)', paddingBottom: '80px', overflowY: 'auto' }}
      >
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation */}
      <BottomTabNav />
    </div>
  );
}
