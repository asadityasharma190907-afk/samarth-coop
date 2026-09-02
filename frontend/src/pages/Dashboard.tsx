import React from 'react';
import { useNavigate } from 'react-router-dom';

export function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('samarth_token');
    navigate('/login');
  };

  return (
    <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
      <h1>Welcome to Dashboard</h1>
      <p>This is a placeholder for the authenticated dashboard.</p>
      <button
        onClick={handleLogout}
        style={{
          marginTop: 'var(--spacing-md)',
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
  );
}
