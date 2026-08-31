import React from 'react';

interface RoleCardProps {
  role: 'citizen' | 'worker';
  title: string;
  description: string;
  selected: boolean;
  onClick: () => void;
}

export function RoleCard({ title, description, selected, onClick }: RoleCardProps) {
  return (
    <div
      onClick={onClick}
      style={{
        flex: 1,
        cursor: 'pointer',
        padding: 'var(--spacing-md)',
        border: selected ? '2px solid var(--color-brand-primary)' : '1px solid var(--color-border-default)',
        borderRadius: 'var(--rounded-lg)',
        backgroundColor: selected ? 'var(--color-surface-overlay)' : 'var(--color-surface-card)',
        boxShadow: selected ? 'var(--shadow-2)' : 'var(--shadow-0)',
        transition: 'all 0.2s ease',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        gap: 'var(--spacing-sm)'
      }}
    >
      <h3 style={{
        margin: 0,
        fontSize: 'var(--font-size-h4)',
        fontWeight: 'var(--font-weight-semibold)',
        color: selected ? 'var(--color-brand-primary-dark)' : 'var(--color-text-primary)'
      }}>
        {title}
      </h3>
      <p style={{
        margin: 0,
        fontSize: 'var(--font-size-caption)',
        color: 'var(--color-text-secondary)',
        lineHeight: 'var(--line-height-caption)'
      }}>
        {description}
      </p>
    </div>
  );
}
