import React, { useState } from 'react';

interface LocationInputProps {
  lat: number;
  lng: number;
  onChange: (lat: number, lng: number) => void;
}

export function LocationInput({ lat, lng, onChange }: LocationInputProps) {
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleGetLocation = () => {
    setErrorMsg('');
    setIsLoading(true);
    
    if (!navigator.geolocation) {
      setErrorMsg('Geolocation is not supported by your browser');
      setIsLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        onChange(position.coords.latitude, position.coords.longitude);
        setIsLoading(false);
      },
      (error) => {
        setIsLoading(false);
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setErrorMsg('Location permission denied. Please enter manually.');
            break;
          case error.POSITION_UNAVAILABLE:
            setErrorMsg('Location information is unavailable.');
            break;
          case error.TIMEOUT:
            setErrorMsg('The request to get user location timed out.');
            break;
          default:
            setErrorMsg('An unknown error occurred.');
            break;
        }
      },
      { timeout: 10000 }
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
      <button
        type="button"
        onClick={handleGetLocation}
        disabled={isLoading}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 'var(--spacing-xs)',
          padding: '10px',
          backgroundColor: 'var(--color-surface-overlay)',
          color: 'var(--color-brand-primary-dark)',
          border: '1px solid var(--color-brand-primary-light)',
          borderRadius: 'var(--rounded-md)',
          fontSize: 'var(--font-size-body-sm)',
          fontWeight: 'var(--font-weight-medium)',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          opacity: isLoading ? 0.7 : 1,
        }}
      >
        <span>📍</span>
        {isLoading ? 'Getting location...' : 'Use my location'}
      </button>

      {errorMsg && (
        <span style={{ color: 'var(--color-status-error)', fontSize: 'var(--font-size-caption)' }}>
          {errorMsg}
        </span>
      )}

      <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <label style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-secondary)' }}>Latitude</label>
          <input
            type="number"
            step="any"
            value={lat}
            onChange={(e) => onChange(parseFloat(e.target.value) || 0, lng)}
            required
            style={{
              padding: '8px',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body-sm)'
            }}
          />
        </div>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <label style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-text-secondary)' }}>Longitude</label>
          <input
            type="number"
            step="any"
            value={lng}
            onChange={(e) => onChange(lat, parseFloat(e.target.value) || 0)}
            required
            style={{
              padding: '8px',
              border: '1px solid var(--color-border-default)',
              borderRadius: 'var(--rounded-md)',
              fontSize: 'var(--font-size-body-sm)'
            }}
          />
        </div>
      </div>
    </div>
  );
}
