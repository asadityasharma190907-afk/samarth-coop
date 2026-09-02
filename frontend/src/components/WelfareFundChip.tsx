import React, { useEffect, useState } from 'react';
import './WelfareFundChip.css';

interface WelfareFundChipProps {
  amount: number | string;
}

export function WelfareFundChip({ amount }: WelfareFundChipProps) {
  const [displayAmount, setDisplayAmount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const targetAmount = Number(amount);

  useEffect(() => {
    // Slight delay for animation entrance
    const showTimer = setTimeout(() => setIsVisible(true), 100);

    // Count-up animation
    let startTimestamp: number | null = null;
    const duration = 500; // 500ms

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);

      // ease-out quartic
      const easeProgress = 1 - Math.pow(1 - progress, 4);

      setDisplayAmount(targetAmount * easeProgress);

      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };

    const animTimer = setTimeout(() => {
      window.requestAnimationFrame(step);
    }, 100);

    return () => {
      clearTimeout(showTimer);
      clearTimeout(animTimer);
    };
  }, [targetAmount]);

  return (
    <div className={`welfare-chip-wrapper ${isVisible ? 'visible' : ''}`}>
      <div className="welfare-chip">
        <span className="welfare-chip-text">
          ₹{displayAmount.toFixed(2)} added to the Cooperative Welfare Fund
        </span>
      </div>
    </div>
  );
}
