import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLoginMutation } from '../hooks/useAuth';

export function Login() {
  const navigate = useNavigate();
  const loginMutation = useLoginMutation();

  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate(
      { phone, password },
      {
        onSuccess: (data) => {
          localStorage.setItem('samarth_token', data.access_token);
          if (data.role === 'worker') {
            navigate('/worker/dashboard');
          } else if (data.role === 'citizen') {
            navigate('/book');
          } else {
            navigate('/federation'); // admin
          }
        },
      },
    );
  };

  const handleQuickLogin = (demoPhone: string) => {
    setPhone(demoPhone);
    setPassword('password123');
    loginMutation.mutate(
      { phone: demoPhone, password: 'password123' },
      {
        onSuccess: (data) => {
          localStorage.setItem('samarth_token', data.access_token);
          if (data.role === 'worker') {
            navigate('/worker/dashboard');
          } else if (data.role === 'citizen') {
            navigate('/dashboard'); // Adjusted to dashboard to match story
          } else {
            navigate('/federation'); // admin
          }
        },
      },
    );
  };

  return (
    <div
      style={{
        maxWidth: '400px',
        margin: '0 auto',
        padding: 'var(--spacing-3xl) var(--spacing-md)',
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-xl)' }}>
        <h1 style={{ fontSize: 'var(--font-size-h2)', marginBottom: 'var(--spacing-xs)' }}>
          Welcome Back
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
          Log in to your Samarth account
        </p>
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
            Phone Number
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
            placeholder="e.g. 9876543210"
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
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
            style={{
              padding: '12px',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body)',
            }}
          />
          {loginMutation.isError && (
            <div
              style={{
                color: 'var(--color-status-error)',
                fontSize: 'var(--font-size-body-sm)',
                marginTop: 'var(--spacing-xs)',
              }}
            >
              {loginMutation.error instanceof Error
                ? loginMutation.error.message
                : 'Invalid credentials. Please try again.'}
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loginMutation.isPending}
          style={{
            marginTop: 'var(--spacing-sm)',
            padding: '12px',
            backgroundColor: 'var(--button-primary-bg)',
            color: 'var(--button-primary-text)',
            border: 'none',
            borderRadius: 'var(--button-primary-radius)',
            fontSize: 'var(--font-size-body)',
            fontWeight: 'var(--font-weight-medium)',
            cursor: loginMutation.isPending ? 'not-allowed' : 'pointer',
            opacity: loginMutation.isPending ? 0.7 : 1,
            transition: 'background-color 0.2s',
          }}
        >
          {loginMutation.isPending ? 'Logging in...' : 'Log in'}
        </button>
      </form>

      <div style={{ marginTop: 'var(--spacing-xl)' }}>
        <p
          style={{
            fontSize: 'var(--font-size-body-sm)',
            color: 'var(--color-text-secondary)',
            textAlign: 'center',
            marginBottom: 'var(--spacing-md)',
          }}
        >
          Fast Testing (Demo Accounts)
        </p>
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', justifyContent: 'center' }}>
          <button
            type="button"
            disabled={loginMutation.isPending}
            onClick={() => handleQuickLogin('9555555555')}
            style={{
              padding: '8px 12px',
              backgroundColor: 'var(--color-surface-card)',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body-sm)',
              cursor: loginMutation.isPending ? 'not-allowed' : 'pointer',
              opacity: loginMutation.isPending ? 0.7 : 1,
            }}
          >
            Citizen
          </button>
          <button
            type="button"
            disabled={loginMutation.isPending}
            onClick={() => handleQuickLogin('9111111111')}
            style={{
              padding: '8px 12px',
              backgroundColor: 'var(--color-surface-card)',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body-sm)',
              cursor: loginMutation.isPending ? 'not-allowed' : 'pointer',
              opacity: loginMutation.isPending ? 0.7 : 1,
            }}
          >
            Worker
          </button>
          <button
            type="button"
            disabled={loginMutation.isPending}
            onClick={() => handleQuickLogin('9000000000')}
            style={{
              padding: '8px 12px',
              backgroundColor: 'var(--color-surface-card)',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body-sm)',
              cursor: loginMutation.isPending ? 'not-allowed' : 'pointer',
              opacity: loginMutation.isPending ? 0.7 : 1,
            }}
          >
            Admin
          </button>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
        <p style={{ fontSize: 'var(--font-size-body-sm)', color: 'var(--color-text-secondary)' }}>
          Don't have an account?{' '}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              navigate('/register');
            }}
            style={{
              color: 'var(--color-brand-primary)',
              textDecoration: 'none',
              fontWeight: 'var(--font-weight-medium)',
            }}
          >
            Register
          </a>
        </p>

        <div style={{ marginTop: 'var(--spacing-md)' }}>
          <a
            href="/why-samarth"
            onClick={(e) => {
              e.preventDefault();
              navigate('/why-samarth');
            }}
            style={{
              fontSize: 'var(--font-size-body-sm)',
              color: 'var(--color-brand-primary)',
              textDecoration: 'none',
              fontWeight: 'var(--font-weight-medium)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 'var(--spacing-xs)',
            }}
          >
            🌿 Why Samarth? (Competitive Comparison) →
          </a>
        </div>
      </div>
    </div>
  );
}
