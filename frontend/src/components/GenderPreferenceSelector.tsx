import React from 'react';
import { Info, User, Users, Sparkles } from 'lucide-react';
import './GenderPreferenceSelector.css';

export type GenderPreference = 'any' | 'female' | 'male';

export interface GenderPreferenceSelectorProps {
  selected: GenderPreference;
  onChange: (preference: GenderPreference) => void;
  disabled?: boolean;
}

export const GENDER_OPTIONS: {
  id: GenderPreference;
  title: string;
  subtitle: string;
  icon: React.ElementType;
}[] = [
  {
    id: 'any',
    title: 'Any Worker',
    subtitle: 'Fastest dispatch',
    icon: Users,
  },
  {
    id: 'female',
    title: 'Female Preferred',
    subtitle: 'Women professionals',
    icon: Sparkles,
  },
  {
    id: 'male',
    title: 'Male Preferred',
    subtitle: 'Men professionals',
    icon: User,
  },
];

export function GenderPreferenceSelector({
  selected,
  onChange,
  disabled = false,
}: GenderPreferenceSelectorProps) {
  return (
    <div className="gender-preference-selector" role="group" aria-label="Worker Gender Preference">
      <div className="gender-preference-header">
        <label className="gender-preference-label">Worker Preference (Optional)</label>
        <span className="gender-preference-badge">Cooperative Inclusion</span>
      </div>

      <div className="gender-preference-grid">
        {GENDER_OPTIONS.map((option) => {
          const Icon = option.icon;
          const isSelected = selected === option.id;

          return (
            <button
              key={option.id}
              type="button"
              className={`gender-chip-btn ${isSelected ? 'selected' : ''}`}
              onClick={() => !disabled && onChange(option.id)}
              disabled={disabled}
              aria-pressed={isSelected}
              data-testid={`gender-chip-${option.id}`}
            >
              <div className="gender-chip-icon-wrapper">
                <Icon size={18} className="gender-chip-icon" />
              </div>
              <div className="gender-chip-content">
                <span className="gender-chip-title">{option.title}</span>
                <span className="gender-chip-subtitle">{option.subtitle}</span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="gender-preference-info">
        <Info size={16} className="gender-info-icon" />
        <span className="gender-info-text">
          Female workers available for cleaning, caregiving & domestic help tasks. Cooperative
          dispatch ensures equal opportunity and safety for all members.
        </span>
      </div>
    </div>
  );
}
