import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Briefcase, CheckCircle, Loader2 } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useProfile } from '../hooks/useProfile';
import { PhotoProofUpload } from '../components/PhotoProofUpload';
import { api } from '../lib/api';

export function WorkerHome() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: profile } = useProfile();
  const [actionError, setActionError] = useState<string | null>(null);

  // Query recent bookings for this worker
  const { data: bookings } = useQuery({
    queryKey: ['workerBookings'],
    queryFn: () => api.get('/bookings'),
  });

  const activeBooking = Array.isArray(bookings)
    ? bookings.find((b: any) => b.status === 'assigned')
    : null;

  const completeMutation = useMutation({
    mutationFn: (bookingId: string) => api.put(`/bookings/${bookingId}/complete`, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workerBookings'] });
      queryClient.invalidateQueries({ queryKey: ['walletSummary'] });
      queryClient.invalidateQueries({ queryKey: ['walletEarnings'] });
    },
    onError: (err: any) => {
      setActionError(err.message || 'Failed to complete booking');
    },
  });

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
            {activeBooking
              ? 'You have an active in-progress job.'
              : 'You are ready to receive job offers.'}
          </p>
        </div>
      </div>

      {/* Active Assigned Job Card (with Photo Proof Uploads) */}
      {activeBooking && (
        <div
          style={{
            backgroundColor: 'var(--color-surface-card)',
            border: '1.5px solid var(--color-brand-primary)',
            borderRadius: 'var(--rounded-lg)',
            padding: 'var(--spacing-lg)',
            marginBottom: 'var(--spacing-xl)',
            boxShadow: 'var(--shadow-1)',
          }}
          data-testid="active-job-card"
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: 'var(--spacing-md)',
              borderBottom: '1px solid var(--color-border-default)',
              paddingBottom: 'var(--spacing-sm)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
              <Briefcase size={20} style={{ color: 'var(--color-brand-primary)' }} />
              <h2 style={{ fontSize: 'var(--font-size-h3)', margin: 0 }}>Active Job in Progress</h2>
            </div>
            <span
              style={{
                fontSize: 'var(--font-size-overline)',
                fontWeight: 600,
                textTransform: 'uppercase',
                padding: '2px 8px',
                borderRadius: 'var(--rounded-full)',
                backgroundColor: 'var(--color-status-info-bg)',
                color: 'var(--color-status-info-text)',
              }}
            >
              Assigned
            </span>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: 'var(--spacing-md)',
              marginBottom: 'var(--spacing-lg)',
            }}
          >
            <div>
              <span
                style={{
                  fontSize: 'var(--font-size-caption)',
                  color: 'var(--color-text-muted)',
                  display: 'block',
                }}
              >
                Service Category
              </span>
              <span
                style={{
                  fontSize: 'var(--font-size-body)',
                  fontWeight: 600,
                  textTransform: 'capitalize',
                }}
              >
                {activeBooking.skill}
              </span>
            </div>
            <div>
              <span
                style={{
                  fontSize: 'var(--font-size-caption)',
                  color: 'var(--color-text-muted)',
                  display: 'block',
                }}
              >
                Direct Earnings (95%)
              </span>
              <span
                style={{
                  fontSize: 'var(--font-size-body)',
                  fontWeight: 700,
                  color: 'var(--color-brand-primary)',
                }}
              >
                ₹{(Number(activeBooking.job_price) * 0.95).toFixed(2)}
              </span>
            </div>
            {activeBooking.description && (
              <div style={{ gridColumn: '1 / -1' }}>
                <span
                  style={{
                    fontSize: 'var(--font-size-caption)',
                    color: 'var(--color-text-muted)',
                    display: 'block',
                  }}
                >
                  Customer Description
                </span>
                <span style={{ fontSize: 'var(--font-size-body-sm)' }}>
                  {activeBooking.description}
                </span>
              </div>
            )}
          </div>

          {/* Photo Proof Upload Step */}
          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <h3
              style={{
                fontSize: 'var(--font-size-body)',
                fontWeight: 600,
                marginBottom: 'var(--spacing-xs)',
              }}
            >
              Work Photo Proof
            </h3>
            <p
              style={{
                fontSize: 'var(--font-size-caption)',
                color: 'var(--color-text-secondary)',
                marginBottom: 'var(--spacing-sm)',
              }}
            >
              Take and upload site photos before starting work and after completion for fair
              verification.
            </p>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: 'var(--spacing-md)',
              }}
            >
              <PhotoProofUpload
                bookingId={activeBooking.booking_id || activeBooking.id}
                photoType="before"
                currentPhotoUrl={activeBooking.before_photo_url}
                onUploaded={() => queryClient.invalidateQueries({ queryKey: ['workerBookings'] })}
              />
              <PhotoProofUpload
                bookingId={activeBooking.booking_id || activeBooking.id}
                photoType="after"
                currentPhotoUrl={activeBooking.after_photo_url}
                onUploaded={() => queryClient.invalidateQueries({ queryKey: ['workerBookings'] })}
              />
            </div>
          </div>

          {actionError && (
            <div
              style={{
                color: 'var(--color-status-error)',
                fontSize: 'var(--font-size-body-sm)',
                marginBottom: 'var(--spacing-sm)',
              }}
            >
              {actionError}
            </div>
          )}

          <button
            type="button"
            className="btn-primary"
            onClick={() => completeMutation.mutate(activeBooking.booking_id || activeBooking.id)}
            disabled={completeMutation.isPending}
            style={{
              width: '100%',
              padding: '14px',
              fontSize: 'var(--font-size-body)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            {completeMutation.isPending ? (
              <>
                <Loader2 size={18} className="spin-icon" /> Completing Job...
              </>
            ) : (
              <>
                <CheckCircle size={18} /> Mark Job as Completed
              </>
            )}
          </button>
        </div>
      )}

      {/* Stats Cards */}
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
