import React from 'react';
import { useLanguage } from '../hooks/useLanguage';

export function LanguageToggle() {
  const { language, setLanguage } = useLanguage();

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        backgroundColor: 'var(--color-surface-overlay)',
        padding: '2px 4px',
        borderRadius: 'var(--rounded-full)',
        border: '1px solid var(--color-border-default)',
      }}
    >
      <button
        onClick={() => setLanguage('en')}
        style={{
          background: language === 'en' ? 'var(--color-surface-card)' : 'transparent',
          color: language === 'en' ? 'var(--color-brand-primary)' : 'var(--color-text-secondary)',
          border: 'none',
          borderRadius: 'var(--rounded-full)',
          padding: '4px 12px',
          fontSize: 'var(--font-size-body-sm)',
          fontWeight:
            language === 'en' ? 'var(--font-weight-semibold)' : 'var(--font-weight-medium)',
          cursor: 'pointer',
          boxShadow: language === 'en' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
          transition: 'all 0.2s',
        }}
      >
        EN
      </button>
      <button
        onClick={() => setLanguage('hi')}
        style={{
          background: language === 'hi' ? 'var(--color-surface-card)' : 'transparent',
          color: language === 'hi' ? 'var(--color-brand-primary)' : 'var(--color-text-secondary)',
          border: 'none',
          borderRadius: 'var(--rounded-full)',
          padding: '4px 12px',
          fontSize: 'var(--font-size-body-sm)',
          fontWeight:
            language === 'hi' ? 'var(--font-weight-semibold)' : 'var(--font-weight-medium)',
          cursor: 'pointer',
          boxShadow: language === 'hi' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
          transition: 'all 0.2s',
        }}
      >
        हिं
      </button>
    </div>
  );
}
