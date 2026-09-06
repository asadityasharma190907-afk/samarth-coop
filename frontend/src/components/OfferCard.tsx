import React, { useState, useEffect, useRef } from 'react';
import { MapPin, Clock, Check, X, AlertTriangle, ShieldAlert } from 'lucide-react';
import { WorkerOfferDetail, useOfferAction } from '../hooks/useOffers';
import { useLanguage } from '../hooks/useLanguage';
import './OfferCard.css';

interface OfferCardProps {
  offer: WorkerOfferDetail;
}

export function OfferCard({ offer }: OfferCardProps) {
  const [secondsLeft, setSecondsLeft] = useState(() =>
    Math.max(0, Math.floor((new Date(offer.expires_at).getTime() - Date.now()) / 1000)),
  );
  const [showConfirm, setShowConfirm] = useState(false);
  const [swipeOffset, setSwipeOffset] = useState(0);
  const [isSwiping, setIsSwiping] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const startXRef = useRef<number | null>(null);
  const actionMutation = useOfferAction();
  const { t } = useLanguage();

  const trustScore = offer.citizen_trust_score ?? 100;
  const showTrustWarning = trustScore < 80;

  const getTrustInfo = () => {
    if (trustScore < 40) {
      return {
        label: 'Restricted citizen',
        badgeClass: 'trust-restricted',
        icon: <ShieldAlert size={15} className="trust-icon" />,
      };
    }
    if (trustScore < 60) {
      return {
        label: 'Confirm before accepting',
        badgeClass: 'trust-caution',
        icon: <AlertTriangle size={15} className="trust-icon" />,
      };
    }
    if (trustScore < 80) {
      return {
        label: 'High cancellation history',
        badgeClass: 'trust-warning',
        icon: <AlertTriangle size={15} className="trust-icon" />,
      };
    }
    return null;
  };

  const trustInfo = getTrustInfo();

  useEffect(() => {
    // Only run timer if less than 90s left initially (or we just run it always to be safe)
    if (secondsLeft <= 0) return;

    const timer = setInterval(() => {
      const remaining = Math.max(
        0,
        Math.floor((new Date(offer.expires_at).getTime() - Date.now()) / 1000),
      );
      setSecondsLeft(remaining);
      if (remaining === 0) {
        clearInterval(timer);
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [offer.expires_at, secondsLeft]);

  const handlePointerDown = (e: React.PointerEvent) => {
    setIsSwiping(true);
    startXRef.current = e.clientX;
    if (cardRef.current) {
      cardRef.current.setPointerCapture(e.pointerId);
    }
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (startXRef.current === null) return;
    const diff = e.clientX - startXRef.current;
    if (diff > 0) {
      setSwipeOffset(Math.min(diff, 150)); // Max drag visual 150px
    }
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    if (startXRef.current !== null) {
      const diff = e.clientX - startXRef.current;
      if (diff > 100) {
        // Trigger swipe to accept shortcut
        handleAccept();
      }
    }
    startXRef.current = null;
    setIsSwiping(false);
    setSwipeOffset(0);
    if (cardRef.current) {
      cardRef.current.releasePointerCapture(e.pointerId);
    }
  };

  const handleAccept = async () => {
    try {
      await actionMutation.mutateAsync({ offerId: offer.id, action: 'accept' });
      setShowConfirm(false);
    } catch (error) {
      console.error('Failed to accept', error);
      alert('Could not accept the offer. Someone else might have taken it!');
    }
  };

  const handleDecline = async () => {
    try {
      await actionMutation.mutateAsync({ offerId: offer.id, action: 'decline' });
    } catch (error) {
      console.error('Failed to decline', error);
    }
  };

  // 90 second threshold for the progress bar
  const showProgress = secondsLeft <= 90;
  const progressPercent = showProgress ? (secondsLeft / 90) * 100 : 100;
  const isDanger = secondsLeft <= 30;

  return (
    <div
      className={`offer-card ${isSwiping ? 'swiping' : ''}`}
      ref={cardRef}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerUp}
      style={{ transform: `translateX(${swipeOffset}px)` }}
    >
      <div
        className="swipe-overlay"
        style={{
          opacity: swipeOffset / 100,
          width: `${swipeOffset}px`,
        }}
      >
        <Check size={32} />
      </div>

      <div className="offer-header">
        <h3 className="offer-skill">{offer.skill}</h3>
        <div className="offer-price">₹{Number(offer.job_price).toFixed(2)}</div>
      </div>

      <div className="offer-meta">
        <div className="offer-meta-item">
          <MapPin size={16} />
          <span>{Number(offer.distance_km).toFixed(1)} km away</span>
        </div>
        <div className="offer-meta-item">
          <Clock size={16} />
          <span>
            Received{' '}
            {new Date(offer.created_at).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>

      {showTrustWarning && trustInfo && (
        <div
          className={`trust-indicator-card ${trustInfo.badgeClass}`}
          data-testid="citizen-trust-warning"
        >
          {trustInfo.icon}
          <span className="trust-title">{trustInfo.label}</span>
          <span className="trust-score-tag">Trust {trustScore}/100</span>
        </div>
      )}

      {showProgress && secondsLeft > 0 && (
        <div className="expiry-section">
          <div className="expiry-progress-container">
            <div
              className={`expiry-progress-bar ${isDanger ? 'danger' : ''}`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className={`expiry-text ${isDanger ? 'danger' : ''}`}>Expires in {secondsLeft}s</div>
        </div>
      )}

      {showConfirm ? (
        <div className="confirm-modal">
          <p>You're taking this job. Your availability will be set to busy.</p>
          <div className="confirm-actions">
            <button
              className="btn-secondary"
              onClick={() => setShowConfirm(false)}
              disabled={actionMutation.isPending}
            >
              Cancel
            </button>
            <button
              className="btn-primary"
              onClick={handleAccept}
              disabled={actionMutation.isPending}
            >
              {actionMutation.isPending ? 'Confirming...' : 'Confirm'}
            </button>
          </div>
        </div>
      ) : (
        <div className="offer-actions">
          <button
            className="btn-secondary"
            style={{ color: 'var(--color-status-error)', borderColor: 'var(--color-status-error)' }}
            onClick={handleDecline}
            disabled={actionMutation.isPending || secondsLeft === 0}
          >
            <X size={18} className="mr-1 inline" /> {t('action.decline')}
          </button>
          <button
            className="btn-primary"
            onClick={() => setShowConfirm(true)}
            disabled={actionMutation.isPending || secondsLeft === 0}
          >
            <Check size={18} className="mr-1 inline" /> {t('action.accept')}
          </button>
        </div>
      )}
    </div>
  );
}
