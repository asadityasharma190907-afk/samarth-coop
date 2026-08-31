import React from 'react';

const SKILLS = [
  'electrician', 'plumber', 'carpenter', 'painter', 'cleaner',
  'gardener', 'cook', 'driver', 'tailor', 'mason'
];

interface SkillChipsProps {
  selectedSkill: string;
  onChange: (skill: string) => void;
}

export function SkillChips({ selectedSkill, onChange }: SkillChipsProps) {
  return (
    <div style={{
      display: 'flex',
      gap: 'var(--spacing-sm)',
      overflowX: 'auto',
      paddingBottom: 'var(--spacing-xs)',
      // hide scrollbar for clean UI but keep it scrollable
      scrollbarWidth: 'none', 
      msOverflowStyle: 'none'
    }}>
      <style>{`
        div::-webkit-scrollbar {
          display: none;
        }
      `}</style>
      
      {SKILLS.map(skill => {
        const isSelected = skill === selectedSkill;
        return (
          <button
            key={skill}
            type="button"
            onClick={() => onChange(skill)}
            style={{
              padding: '8px 16px',
              borderRadius: 'var(--rounded-full)',
              border: '1px solid',
              borderColor: isSelected ? 'var(--color-brand-primary)' : 'var(--color-border-default)',
              backgroundColor: isSelected ? 'var(--color-brand-primary)' : 'var(--color-surface-bg)',
              color: isSelected ? 'var(--color-text-on-brand)' : 'var(--color-text-secondary)',
              fontSize: 'var(--font-size-body-sm)',
              fontWeight: 'var(--font-weight-medium)',
              cursor: 'pointer',
              textTransform: 'capitalize',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease',
              outline: 'none'
            }}
          >
            {skill}
          </button>
        );
      })}
    </div>
  );
}
