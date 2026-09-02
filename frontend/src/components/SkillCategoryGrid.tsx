import React from 'react';
import {
  Zap,
  Wrench,
  Hammer,
  Paintbrush,
  Sparkles,
  WashingMachine,
  TreePine,
  Bug,
  Car,
  HardHat,
} from 'lucide-react';
import './SkillCategoryGrid.css';

export const SKILL_CATEGORIES = [
  { id: 'electrician', label: 'Electrician', icon: Zap },
  { id: 'plumber', label: 'Plumber', icon: Wrench },
  { id: 'carpenter', label: 'Carpenter', icon: Hammer },
  { id: 'painter', label: 'Painter', icon: Paintbrush },
  { id: 'cleaner', label: 'Cleaner', icon: Sparkles },
  { id: 'appliance repair', label: 'Appliance Repair', icon: WashingMachine },
  { id: 'gardener', label: 'Gardener', icon: TreePine },
  { id: 'pest control', label: 'Pest Control', icon: Bug },
  { id: 'mechanic', label: 'Mechanic', icon: Car },
  { id: 'mason', label: 'Mason', icon: HardHat },
];

interface Props {
  selectedSkill: string | null;
  onSelect: (skill: string) => void;
}

export function SkillCategoryGrid({ selectedSkill, onSelect }: Props) {
  return (
    <div className="skill-grid">
      {SKILL_CATEGORIES.map((category) => {
        const Icon = category.icon;
        const isSelected = selectedSkill === category.id;

        return (
          <button
            key={category.id}
            onClick={() => onSelect(category.id)}
            className={`skill-card ${isSelected ? 'selected' : ''}`}
            type="button"
          >
            <Icon />
            <span className="skill-label">{category.label}</span>
          </button>
        );
      })}
    </div>
  );
}
