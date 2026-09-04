import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useBookings } from '../hooks/useBooking';

export function Dashboard() {
  const navigate = useNavigate();
  const { data: bookings, isLoading, isError } = useBookings();

  const handleLogout = () => {
    localStorage.removeItem('samarth_token');
    navigate('/login');
  };

  return (
    <div style={{ padding: 'var(--spacing-xl)', maxWidth: '600px', margin: '0 auto' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 'var(--spacing-xl)',
        }}
      >
        <h1 style={{ fontSize: 'var(--font-size-h2)', margin: 0 }}>My Bookings</h1>
        <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
          <button
            onClick={() => navigate('/book')}
            style={{
              padding: '8px 16px',
              backgroundColor: 'var(--button-primary-bg)',
              color: 'var(--button-primary-text)',
              border: 'none',
              borderRadius: 'var(--button-primary-radius)',
              cursor: 'pointer',
              fontWeight: 'var(--font-weight-medium)',
            }}
          >
            Book New Service
          </button>
          <button
            onClick={handleLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: 'var(--button-secondary-bg)',
              color: 'var(--button-secondary-text)',
              border: 'var(--button-secondary-border)',
              borderRadius: 'var(--button-secondary-radius)',
              cursor: 'pointer',
            }}
          >
            Log out
          </button>
        </div>
      </div>

      {isLoading ? (
        <p>Loading bookings...</p>
      ) : isError ? (
        <p style={{ color: 'var(--color-status-error)' }}>Failed to load bookings.</p>
      ) : bookings && bookings.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {bookings.map((booking) => (
            <div
              key={booking.booking_id}
              style={{
                padding: 'var(--spacing-md)',
                backgroundColor: 'var(--color-surface-card)',
                border: '1px solid var(--color-border-default)',
                borderRadius: 'var(--rounded-md)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <h3
                  style={{
                    fontSize: 'var(--font-size-body)',
                    marginBottom: 'var(--spacing-xs)',
                    textTransform: 'capitalize',
                    margin: 0,
                  }}
                >
                  {booking.skill}
                </h3>
                <p
                  style={{
                    fontSize: 'var(--font-size-body-sm)',
                    color: 'var(--color-text-secondary)',
                    margin: 0,
                  }}
                >
                  Price: ₹{booking.job_price} • Date:{' '}
                  {new Date(booking.created_at).toLocaleDateString()}
                </p>
              </div>
              <span
                style={{
                  padding: '4px 8px',
                  borderRadius: 'var(--rounded-full)',
                  fontSize: 'var(--font-size-body-sm)',
                  fontWeight: 'var(--font-weight-medium)',
                  backgroundColor:
                    booking.status === 'completed'
                      ? 'var(--color-status-success-bg)'
                      : booking.status === 'pending'
                        ? 'var(--color-status-info-bg)'
                        : booking.status === 'cancelled'
                          ? 'var(--color-status-error-bg)'
                          : 'var(--color-surface-overlay)',
                  color:
                    booking.status === 'completed'
                      ? 'var(--color-status-success)'
                      : booking.status === 'pending'
                        ? 'var(--color-status-info)'
                        : booking.status === 'cancelled'
                          ? 'var(--color-status-error)'
                          : 'var(--color-text-primary)',
                }}
              >
                {booking.status}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ color: 'var(--color-text-secondary)' }}>You have no recent bookings.</p>
      )}
    </div>
  );
}
