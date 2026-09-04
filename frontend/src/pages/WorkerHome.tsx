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

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 'var(--spacing-xl)',
        }}
      >
        <div>
          <h1 style={{ fontSize: 'var(--font-size-h2)', margin: 0 }}>
            Welcome back, {profile?.name || 'Worker'}
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
            You are ready to receive job offers.
          </p>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--spacing-md)',
          marginBottom: 'var(--spacing-xl)',
        }}
      >
        <div
          style={{
            backgroundColor: 'var(--color-surface-card)',
            padding: 'var(--spacing-lg)',
            borderRadius: 'var(--rounded-lg)',
            border: '1px solid var(--color-border-default)',
            boxShadow: 'var(--shadow-1)',
          }}
        >
          <h3
            style={{
              color: 'var(--color-text-secondary)',
              fontSize: 'var(--font-size-body-sm)',
              margin: 0,
            }}
          >
            Current Rating
          </h3>
          <p
            style={{
              fontSize: 'var(--font-size-h1)',
              fontWeight: 'var(--font-weight-bold)',
              color: 'var(--color-brand-primary)',
              margin: 'var(--spacing-xs) 0 0',
            }}
          >
            {profile?.rating ? Number(profile.rating).toFixed(1) : 'New'}
          </p>
        </div>

        <div
          style={{
            backgroundColor: 'var(--color-surface-card)',
            padding: 'var(--spacing-lg)',
            borderRadius: 'var(--rounded-lg)',
            border: '1px solid var(--color-border-default)',
            boxShadow: 'var(--shadow-1)',
          }}
        >
          <h3
            style={{
              color: 'var(--color-text-secondary)',
              fontSize: 'var(--font-size-body-sm)',
              margin: 0,
            }}
          >
            Skill Profile
          </h3>
          <p
            style={{
              fontSize: 'var(--font-size-h2)',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--color-text-primary)',
              margin: 'var(--spacing-xs) 0 0',
              textTransform: 'capitalize',
            }}
          >
            {profile?.skill || 'Loading...'}
          </p>
        </div>
      </div>

      <div className="mobile-logout" style={{ marginTop: 'var(--spacing-xl)' }}>
        <style>{`
          @media (min-width: 1024px) {
            .mobile-logout {
              display: none !important;
            }
          }
        `}</style>
        <button
          className="btn-secondary"
          onClick={handleLogout}
          style={{
            width: '100%',
            color: 'var(--color-status-error)',
            borderColor: 'var(--color-status-error)',
          }}
        >
          Log out
        </button>
      </div>
    </>
  );
}
