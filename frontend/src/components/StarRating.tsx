import React, { useState } from 'react';
import { Star } from 'lucide-react';
import './StarRating.css';

interface StarRatingProps {
  onRate: (rating: number) => void;
  disabled?: boolean;
}

export function StarRating({ onRate, disabled = false }: StarRatingProps) {
  const [hoverRating, setHoverRating] = useState(0);
  const [selectedRating, setSelectedRating] = useState(0);

  const handleMouseEnter = (index: number) => {
    if (!disabled) setHoverRating(index);
  };

  const handleMouseLeave = () => {
    if (!disabled) setHoverRating(0);
  };

  const handleClick = (index: number) => {
    if (!disabled) {
      setSelectedRating(index);
      onRate(index);
    }
  };

  return (
    <div className="star-rating" onMouseLeave={handleMouseLeave}>
      {[1, 2, 3, 4, 5].map((index) => (
        <button
          key={index}
          type="button"
          className={`star-btn ${index <= (hoverRating || selectedRating) ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
          onMouseEnter={() => handleMouseEnter(index)}
          onClick={() => handleClick(index)}
          disabled={disabled}
        >
          <Star 
            size={24} 
            className="star-icon"
            fill={index <= (hoverRating || selectedRating) ? 'currentColor' : 'none'} 
          />
        </button>
      ))}
    </div>
  );
}
