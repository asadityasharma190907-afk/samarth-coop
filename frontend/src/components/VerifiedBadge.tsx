import React from 'react';
import { ShieldCheck } from 'lucide-react';
import './VerifiedBadge.css';

interface VerifiedBadgeProps {
  className?: string;
}

export function VerifiedBadge({ className = '' }: VerifiedBadgeProps) {
  return (
    <span className={`badge-verified ${className}`}>
      <ShieldCheck size={14} /> Society Verified
    </span>
  );
}
