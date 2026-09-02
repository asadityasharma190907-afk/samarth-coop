import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRegisterMutation } from '../hooks/useAuth';
import { RoleCard } from '../components/RoleCard';
import { SkillChips } from '../components/SkillChips';
import { LocationInput } from '../components/LocationInput';

export function Register() {
  const navigate = useNavigate();
  const registerMutation = useRegisterMutation();

  const [role, setRole] = useState<'citizen' | 'worker'>('citizen');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [skill, setSkill] = useState('electrician'); // Default worker skill

  const [lat, setLat] = useState<number>(0);
  const [lng, setLng] = useState<number>(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const payload: any = {
      role,
      name,
      phone,
      password,
    };

    if (role === 'worker') {
      payload.skill = skill;
      payload.lat = lat;
      payload.lng = lng;
    }

    registerMutation.mutate(payload, {
      onSuccess: (data) => {
        localStorage.setItem('samarth_token', data.access_token);
        if (role === 'worker') {
          navigate('/worker/dashboard');
        } else {
          navigate('/dashboard');
        }
      },
    });
  };

  return (
    <div
      style={{
        maxWidth: '400px',
        margin: '0 auto',
        padding: 'var(--spacing-xl) var(--spacing-md)',
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-xl)' }}>
        <h1 style={{ fontSize: 'var(--font-size-h2)', marginBottom: 'var(--spacing-xs)' }}>
          Join Samarth
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
          Create your account to get started
        </p>
      </div>

      <div style={{ display: 'flex', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-lg)' }}>
        <RoleCard
          role="citizen"
          title="Citizen"
          description="Book services"
          selected={role === 'citizen'}
          onClick={() => setRole('citizen')}
        />
        <RoleCard
          role="worker"
          title="Worker"
          description="Offer services"
          selected={role === 'worker'}
          onClick={() => setRole('worker')}
        />
      </div>

      <form
        onSubmit={handleSubmit}
        style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
          <label
            style={{
              fontSize: 'var(--font-size-body-sm)',
              fontWeight: 'var(--font-weight-medium)',
            }}
          >
            Full Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="e.g. Ravi Sharma"
            style={{
              padding: '12px',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body)',
            }}
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
          <label
            style={{
              fontSize: 'var(--font-size-body-sm)',
              fontWeight: 'var(--font-weight-medium)',
            }}
          >
            Phone Number
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
            minLength={10}
            maxLength={15}
            placeholder="e.g. 9876543210"
            style={{
              padding: '12px',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body)',
            }}
          />
        </div>

        {role === 'worker' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
              <label
                style={{
                  fontSize: 'var(--font-size-body-sm)',
                  fontWeight: 'var(--font-weight-medium)',
                }}
              >
                Skill
              </label>
              <SkillChips selectedSkill={skill} onChange={setSkill} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
              <label
                style={{
                  fontSize: 'var(--font-size-body-sm)',
                  fontWeight: 'var(--font-weight-medium)',
                }}
              >
                Location
              </label>
              <LocationInput
                lat={lat}
                lng={lng}
                onChange={(newLat, newLng) => {
                  setLat(newLat);
                  setLng(newLng);
                }}
              />
            </div>
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
          <label
            style={{
              fontSize: 'var(--font-size-body-sm)',
              fontWeight: 'var(--font-weight-medium)',
            }}
          >
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            placeholder="••••••••"
            style={{
              padding: '12px',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body)',
            }}
          />
        </div>

        {registerMutation.isError && (
          <div style={{ color: 'var(--color-status-error)', fontSize: 'var(--font-size-body-sm)' }}>
            {registerMutation.error instanceof Error
              ? registerMutation.error.message
              : 'Registration failed. Please try again.'}
          </div>
        )}

        <button
          type="submit"
          disabled={registerMutation.isPending}
          style={{
            marginTop: 'var(--spacing-sm)',
            padding: '12px',
            backgroundColor: 'var(--button-primary-bg)',
            color: 'var(--button-primary-text)',
            border: 'none',
            borderRadius: 'var(--button-primary-radius)',
            fontSize: 'var(--font-size-body)',
            fontWeight: 'var(--font-weight-medium)',
            cursor: registerMutation.isPending ? 'not-allowed' : 'pointer',
            opacity: registerMutation.isPending ? 0.7 : 1,
            transition: 'background-color 0.2s',
          }}
        >
          {registerMutation.isPending ? 'Registering...' : 'Register'}
        </button>
      </form>

      <div style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
        <p style={{ fontSize: 'var(--font-size-body-sm)', color: 'var(--color-text-secondary)' }}>
          Already have an account?{' '}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              navigate('/login');
            }}
            style={{
              color: 'var(--color-brand-primary)',
              textDecoration: 'none',
              fontWeight: 'var(--font-weight-medium)',
            }}
          >
            Log in
          </a>
        </p>
      </div>
    </div>
  );
}
