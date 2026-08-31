import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ShieldCheck, Star, MapPin, Search } from 'lucide-react';
import { useBooking } from '../hooks/useBooking';
import { WelfareFundChip } from '../components/WelfareFundChip';
import './BookingStatus.css';

export function BookingStatus() {
  const { id } = useParams<{ id: string }>();
  const { data: booking, isLoading, isError } = useBooking(id);
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="status-container">
        <div className="status-card">
          <h2 className="status-title">Loading...</h2>
        </div>
      </div>
    );
  }

  if (isError || !booking) {
    return (
      <div className="status-container">
        <div className="status-card">
          <h2 className="status-title">Booking not found</h2>
          <button className="btn-primary mt-4" onClick={() => navigate('/book')}>
            Book a new service
          </button>
        </div>
      </div>
    );
  }

  const isSearching = booking.status === 'pending' || booking.status === 'offered';
  const isAssigned = booking.status === 'assigned';
  const isCancelled = booking.status === 'cancelled';
  const isCompleted = booking.status === 'completed';

  return (
    <div className="status-container">
      {isSearching && (
        <div className="status-card">
          <div className="pulse-ring">
            <Search className="w-8 h-8 text-brand-primary" />
          </div>
          <h2 className="status-title">Finding a cooperative worker for you...</h2>
          <p className="status-subtitle">
            We are looking for the best {booking.skill} nearby. Please wait.
          </p>
        </div>
      )}

      {isAssigned && booking.assigned_worker && (
        <div className="worker-card animate-fade-in">
          <div className="worker-header">
            <div>
              <h2 className="worker-name">{booking.assigned_worker.name}</h2>
              <p className="worker-skill">{booking.assigned_worker.skill}</p>
            </div>
            {booking.assigned_worker.verified && (
              <span className="badge-verified">
                <ShieldCheck size={14} /> Society Verified
              </span>
            )}
          </div>

          <div className="worker-stats">
            <div className="stat-item">
              <Star size={16} className="stat-icon" />
              {booking.assigned_worker.rating ? booking.assigned_worker.rating.toFixed(1) : 'New'}
            </div>
            <div className="stat-item">
              <MapPin size={16} className="stat-icon" />
              {booking.assigned_worker.distance_km} km away
            </div>
          </div>
          
          <div className="action-buttons mt-6">
            <button className="btn-secondary" onClick={() => alert('Feature coming soon: Call worker')}>
              Call Worker
            </button>
          </div>
        </div>
      )}

      {isCancelled && (
        <div className="status-card">
          <h2 className="status-title text-status-error">No workers available right now</h2>
          <p className="status-subtitle mb-6">
            All nearby {booking.skill}s are currently busy. Please try again later.
          </p>
          <button className="btn-primary" onClick={() => navigate('/book')}>
            Try Again
          </button>
        </div>
      )}
      
      {isCompleted && (
        <div className="status-card">
          <h2 className="status-title text-status-success">Job Completed</h2>
          <p className="status-subtitle mb-6">
            Thank you for using Samarth!
          </p>
          <WelfareFundChip amount={booking.platform_fee || 0} />
          <div className="mt-8">
            <button className="btn-primary" onClick={() => navigate('/book')}>
              Book Another Service
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
