import React from 'react';
import { useProfile } from '../hooks/useProfile';
import { InsuranceStatusCard } from '../components/InsuranceStatusCard';

export function WorkerProfile() {
  const { data: profile, isLoading, isError } = useProfile();

  if (isLoading) {
    return (
      <div>
        <h1 style={{ fontSize: 'var(--font-size-h2)', margin: 0 }}>My Profile</h1>
        <p>Loading profile data...</p>
      </div>
    );
  }

  if (isError || !profile) {
    return (
      <div>
        <h1 style={{ fontSize: 'var(--font-size-h2)', margin: 0 }}>My Profile</h1>
        <p style={{ color: 'var(--color-status-error)' }}>Failed to load profile.</p>
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ fontSize: 'var(--font-size-h2)', margin: '0 0 var(--spacing-xl)' }}>
        My Profile
      </h1>

      <div
        style={{
          backgroundColor: 'var(--color-surface-card)',
          borderRadius: 'var(--rounded-lg)',
          border: '1px solid var(--color-border-default)',
          boxShadow: 'var(--shadow-1)',
          overflow: 'hidden',
        }}
      >
        {/* Profile Header */}
        <div
          style={{
            padding: 'var(--spacing-lg)',
            borderBottom: '1px solid var(--color-border-default)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-md)',
          }}
        >
          <div
            style={{
              width: '64px',
              height: '64px',
              backgroundColor: 'var(--color-brand-primary)',
              borderRadius: 'var(--rounded-full)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-surface-bg)',
              fontSize: 'var(--font-size-h2)',
              fontWeight: 'var(--font-weight-bold)',
            }}
          >
            {profile.name ? profile.name.charAt(0).toUpperCase() : 'W'}
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: 'var(--font-size-h3)' }}>
              {profile.name || 'Worker'}
            </h2>
            <p
              style={{
                margin: 'var(--spacing-xs) 0 0',
                color: 'var(--color-text-secondary)',
                textTransform: 'capitalize',
              }}
            >
              {profile.skill} Worker
            </p>
          </div>
        </div>

        {/* Profile Details Grid */}
        <div
          style={{
            padding: 'var(--spacing-lg)',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: 'var(--spacing-lg)',
          }}
        >
          <div>
            <h3
              style={{
                margin: '0 0 var(--spacing-xs)',
                fontSize: 'var(--font-size-body-sm)',
                color: 'var(--color-text-secondary)',
              }}
            >
              Phone Number
            </h3>
            <p style={{ margin: 0, fontSize: 'var(--font-size-body)' }}>+91 {profile.phone}</p>
          </div>

          <div>
            <h3
              style={{
                margin: '0 0 var(--spacing-xs)',
                fontSize: 'var(--font-size-body-sm)',
                color: 'var(--color-text-secondary)',
              }}
            >
              Verification Status
            </h3>
            <span
              style={{
                display: 'inline-block',
                padding: '4px 8px',
                borderRadius: 'var(--rounded-full)',
                fontSize: 'var(--font-size-caption)',
                fontWeight: 'var(--font-weight-medium)',
                backgroundColor:
                  profile.verification_status === 'verified'
                    ? 'var(--color-status-success-bg)'
                    : 'var(--color-status-warning-bg)',
                color:
                  profile.verification_status === 'verified'
                    ? 'var(--color-status-success)'
                    : 'var(--color-status-warning)',
                textTransform: 'capitalize',
              }}
            >
              {profile.verification_status}
            </span>
          </div>

          <div>
            <h3
              style={{
                margin: '0 0 var(--spacing-xs)',
                fontSize: 'var(--font-size-body-sm)',
                color: 'var(--color-text-secondary)',
              }}
            >
              Experience
            </h3>
            <p style={{ margin: 0, fontSize: 'var(--font-size-body)' }}>
              {profile.experience_years ? `${profile.experience_years} years` : 'Not specified'}
            </p>
          </div>

          <div>
            <h3
              style={{
                margin: '0 0 var(--spacing-xs)',
                fontSize: 'var(--font-size-body-sm)',
                color: 'var(--color-text-secondary)',
              }}
            >
              Languages
            </h3>
            <p style={{ margin: 0, fontSize: 'var(--font-size-body)' }}>
              {profile.languages_spoken || 'Not specified'}
            </p>
          </div>

          <div style={{ gridColumn: '1 / -1' }}>
            <h3
              style={{
                margin: '0 0 var(--spacing-xs)',
                fontSize: 'var(--font-size-body-sm)',
                color: 'var(--color-text-secondary)',
              }}
            >
              Local Address
            </h3>
            <p style={{ margin: 0, fontSize: 'var(--font-size-body)' }}>
              {profile.local_address || 'Not specified'}
            </p>
          </div>
        </div>
      </div>

      {profile.verification_status === 'verified' && (
        <InsuranceStatusCard
          completedJobs={profile.completed_jobs_count}
          lifetimeContribution={profile.lifetime_welfare_fund_contribution}
        />
      )}
    </div>
  );
}
