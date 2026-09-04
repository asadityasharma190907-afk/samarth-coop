import React from 'react';
import { ShieldCheck, Clock, ShieldAlert } from 'lucide-react';
import './VerifiedBadge.css';

interface VerifiedBadgeProps {
  status?: 'verified' | 'pending' | 'unverified' | string;
  type?: 'police' | 'society';
  className?: string;
}

export function VerifiedBadge({
  status = 'verified',
  type = 'police',
  className = '',
}: VerifiedBadgeProps) {
  if (status === 'pending') {
    return (
      <span className={`badge-pending ${className}`}>
        <Clock size={14} /> Verification Pending
      </span>
    );
  }

  if (status === 'unverified' || status === 'rejected') {
    return (
      <span className={`badge-unverified ${className}`}>
        <ShieldAlert size={14} /> Unverified
      </span>
    );
  }

  const label = type === 'police' ? 'Police Verified' : 'Society Verified';

  return (
    <span className={`badge-verified ${className}`}>
      <ShieldCheck size={14} /> {label}
    </span>
  );
}
