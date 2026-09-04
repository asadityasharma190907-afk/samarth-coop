import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock } from 'lucide-react';
import { useProfile } from '../hooks/useProfile';

export function WorkerHome() {
  const navigate = useNavigate();
  const { data: profile } = useProfile();

  const handleLogout = () => {
    localStorage.removeItem('samarth_token');
    navigate('/login');
  };

  return (
    <>
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
            Your profile is currently under cooperative review. You will start receiving job offers
            once verified by the society administrator.
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
    </>
  );
}
