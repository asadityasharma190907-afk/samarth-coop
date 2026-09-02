import React, { useEffect, useState } from 'react';
import './StatCounter.css';

interface StatCounterProps {
  value: number;
  label: string;
  prefix?: string;
  duration?: number;
  isViolet?: boolean;
}

export function StatCounter({
  value,
  label,
  prefix = '',
  duration = 1500,
  isViolet = false,
}: StatCounterProps) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTimestamp: number | null = null;
    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);

      // easeOutQuart curve
      const easeProgress = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeProgress * value));

      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        setCount(value);
      }
    };

    window.requestAnimationFrame(step);
  }, [value, duration]);

  return (
    <div className={`stat-counter-card ${isViolet ? 'violet-gradient' : ''}`}>
      <div className="stat-value">
        {prefix}
        {count.toLocaleString('en-IN')}
      </div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
