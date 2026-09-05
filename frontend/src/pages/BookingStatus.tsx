import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MapPin, Search, Star, AlertTriangle } from 'lucide-react';
import { useBooking, useDisputeBooking } from '../hooks/useBooking';
import { DisputeModal } from '../components/DisputeModal';
import { WelfareFundChip } from '../components/WelfareFundChip';
import { VerifiedBadge } from '../components/VerifiedBadge';
import { StarRating } from '../components/StarRating';
import { useLanguage } from '../hooks/useLanguage';
import { PricingBreakdown } from '../components/PricingBreakdown';
import { PhotoProofCard } from '../components/PhotoProofCard';
import { api } from '../lib/api';
import './BookingStatus.css';

export function BookingStatus() {
  const { id } = useParams<{ id: string }>();
  const { data: booking, isLoading, isError } = useBooking(id);
  const navigate = useNavigate();
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const [isSubmittingRating, setIsSubmittingRating] = useState(false);
  const [isDisputeModalOpen, setIsDisputeModalOpen] = useState(false);
  const { t } = useLanguage();

  const disputeMutation = useDisputeBooking(id || '');

  const handleDispute = (reason: string) => {
    disputeMutation.mutate(reason, {
      onSuccess: () => setIsDisputeModalOpen(false),
      onError: (err: any) => alert(err.message || 'Failed to submit dispute'),
    });
  };

  const handleRate = async (rating: number) => {
    if (!id || isSubmittingRating) return;
    setIsSubmittingRating(true);
    try {
      await api.post(`/bookings/${id}/rating`, { rating });
      setRatingSubmitted(true);
    } catch (err: any) {
      alert(err.message || 'Failed to submit rating');
    } finally {
      setIsSubmittingRating(false);
    }
  };

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
  const isDisputed = booking.status === 'disputed';

  return (
    <div className="status-container">
      <PricingBreakdown booking={booking} />
      {isSearching && (
        <div className="status-card">
          <div className="pulse-ring">
            <Search className="w-8 h-8 text-brand-primary" />
          </div>
          <h2 className="status-title">{t('status.pending')}</h2>
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
            <VerifiedBadge
              status={
                booking.assigned_worker.verification_status ||
                (booking.assigned_worker.verified ? 'verified' : 'pending')
              }
            />
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

          {(booking.before_photo_url || booking.after_photo_url) && (
            <PhotoProofCard
              beforePhotoUrl={booking.before_photo_url}
              afterPhotoUrl={booking.after_photo_url}
            />
          )}

          <div className="action-buttons mt-6">
            <button
              className="btn-secondary"
              onClick={() => alert('Feature coming soon: Call worker')}
            >
              Call Worker
            </button>
            <button
              className="btn-secondary"
              style={{ color: 'var(--color-status-error)', fontWeight: 500 }}
              onClick={() => setIsDisputeModalOpen(true)}
            >
              Report Issue
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
          <p className="status-subtitle mb-6">Thank you for using Samarth!</p>
          <WelfareFundChip amount={booking.platform_fee || 0} />

          <PhotoProofCard
            beforePhotoUrl={booking.before_photo_url}
            afterPhotoUrl={booking.after_photo_url}
          />

          <div className="mt-8 mb-4">
            {!booking.rating && !ratingSubmitted ? (
              <div className="rating-section">
                <p className="rating-prompt">Rate your experience</p>
                <StarRating onRate={handleRate} disabled={isSubmittingRating} />
              </div>
            ) : (
              <div className="text-status-success font-medium">Rating submitted. Thank you.</div>
            )}
          </div>
          <div className="mt-8 flex" style={{ gap: 'var(--spacing-3)' }}>
            <button className="btn-primary flex-1" onClick={() => navigate('/book')}>
              Book Another Service
            </button>
            <button
              className="btn-secondary flex-1"
              style={{ color: 'var(--color-status-error)', fontWeight: 500 }}
              onClick={() => setIsDisputeModalOpen(true)}
            >
              Report Issue
            </button>
          </div>
        </div>
      )}
      {isDisputed && (
        <div className="status-card" style={{ borderColor: 'var(--color-status-error)' }}>
          <div className="pulse-ring" style={{ background: 'rgba(239, 68, 68, 0.1)' }}>
            <AlertTriangle className="w-8 h-8 text-status-error" />
          </div>
          <h2
            className="status-title text-status-error"
            style={{ color: 'var(--color-status-error)' }}
          >
            Under Cooperative Review — Dispute Registered
          </h2>
          <p className="status-subtitle mb-6">{booking.dispute_reason}</p>
          <button className="btn-primary" onClick={() => navigate('/book')}>
            Book Another Service
          </button>
        </div>
      )}

      <DisputeModal
        isOpen={isDisputeModalOpen}
        onClose={() => setIsDisputeModalOpen(false)}
        onSubmit={handleDispute}
        isSubmitting={disputeMutation.isPending}
      />
    </div>
  );
}
