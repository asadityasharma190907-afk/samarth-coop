import React, { useState } from 'react';
import { AlertCircle, X } from 'lucide-react';
import './DisputeModal.css';

interface DisputeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (reason: string) => void;
  isSubmitting: boolean;
}

export function DisputeModal({ isOpen, onClose, onSubmit, isSubmitting }: DisputeModalProps) {
  const [reason, setReason] = useState('');
  const maxLength = 500;

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (reason.trim().length > 0 && !isSubmitting) {
      onSubmit(reason.trim());
    }
  };

  const isSubmitDisabled = reason.trim().length === 0 || isSubmitting;

  return (
    <div className="dispute-modal-overlay">
      <div className="dispute-modal-content animate-fade-in">
        <button className="dispute-modal-close" onClick={onClose} aria-label="Close">
          <X size={20} />
        </button>

        <div className="dispute-modal-header">
          <AlertCircle className="dispute-modal-icon" size={24} />
          <h2>Report an Issue</h2>
        </div>

        <p className="dispute-modal-description">
          Please explain the issue you encountered. This will halt the booking and notify
          cooperative administrators for review.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="dispute-input-group">
            <textarea
              className="dispute-textarea"
              placeholder="e.g. The worker did not show up, asked for off-platform payment, etc."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              maxLength={maxLength}
              disabled={isSubmitting}
              autoFocus
            />
            <div className="dispute-char-count">
              {reason.length} / {maxLength}
            </div>
          </div>

          <div className="dispute-modal-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button type="submit" className="btn-danger" disabled={isSubmitDisabled}>
              {isSubmitting ? 'Submitting...' : 'Submit Dispute'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
