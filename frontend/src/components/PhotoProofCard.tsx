import React, { useState } from 'react';
import { ShieldCheck, Image as ImageIcon, X } from 'lucide-react';
import './PhotoProofCard.css';

export interface PhotoProofCardProps {
  beforePhotoUrl?: string | null;
  afterPhotoUrl?: string | null;
  title?: string;
}

export function PhotoProofCard({
  beforePhotoUrl,
  afterPhotoUrl,
  title = 'Work Verification & Photo Proof',
}: PhotoProofCardProps) {
  const [zoomedImage, setZoomedImage] = useState<{ src: string; title: string } | null>(null);

  const getFullImageUrl = (url: string) => {
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    const baseURL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
    return `${baseURL}${url}`;
  };

  const hasAnyPhoto = Boolean(beforePhotoUrl || afterPhotoUrl);

  return (
    <div className="photo-proof-card" data-testid="photo-proof-card">
      <div className="photo-proof-card-header">
        <div className="photo-proof-card-title-group">
          <ShieldCheck size={20} className="photo-proof-shield-icon" />
          <h3 className="photo-proof-card-title">{title}</h3>
        </div>
        <span className="photo-proof-card-badge">
          {hasAnyPhoto ? 'Verified Proof' : 'No Proof Uploaded'}
        </span>
      </div>

      <p className="photo-proof-card-desc">
        Cooperative transparency guarantee: Workers capture before and after photos to document
        quality of service and protect both parties.
      </p>

      <div className="photo-proof-grid">
        {/* Before Photo Item */}
        <div className="photo-proof-item">
          <span className="photo-proof-item-label">Before Starting Work</span>
          {beforePhotoUrl ? (
            <div
              className="photo-proof-item-img-wrap"
              onClick={() =>
                setZoomedImage({
                  src: getFullImageUrl(beforePhotoUrl),
                  title: 'Before Work Photo',
                })
              }
              role="button"
              tabIndex={0}
              aria-label="Zoom Before Work Photo"
            >
              <img
                src={getFullImageUrl(beforePhotoUrl)}
                alt="Before work proof"
                className="photo-proof-img"
              />
              <span className="photo-proof-zoom-hint">Click to enlarge</span>
            </div>
          ) : (
            <div className="photo-proof-empty">
              <ImageIcon size={24} className="photo-proof-empty-icon" />
              <span>No before photo uploaded</span>
            </div>
          )}
        </div>

        {/* After Photo Item */}
        <div className="photo-proof-item">
          <span className="photo-proof-item-label">After Completion</span>
          {afterPhotoUrl ? (
            <div
              className="photo-proof-item-img-wrap"
              onClick={() =>
                setZoomedImage({
                  src: getFullImageUrl(afterPhotoUrl),
                  title: 'After Completion Photo',
                })
              }
              role="button"
              tabIndex={0}
              aria-label="Zoom After Completion Photo"
            >
              <img
                src={getFullImageUrl(afterPhotoUrl)}
                alt="After completion proof"
                className="photo-proof-img"
              />
              <span className="photo-proof-zoom-hint">Click to enlarge</span>
            </div>
          ) : (
            <div className="photo-proof-empty">
              <ImageIcon size={24} className="photo-proof-empty-icon" />
              <span>No after photo uploaded</span>
            </div>
          )}
        </div>
      </div>

      {/* Lightbox / Zoom Modal */}
      {zoomedImage && (
        <div className="photo-zoom-modal-backdrop" onClick={() => setZoomedImage(null)}>
          <div className="photo-zoom-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="photo-zoom-modal-header">
              <span className="photo-zoom-modal-title">{zoomedImage.title}</span>
              <button
                type="button"
                className="photo-zoom-close-btn"
                onClick={() => setZoomedImage(null)}
                aria-label="Close enlarged photo"
              >
                <X size={20} />
              </button>
            </div>
            <img src={zoomedImage.src} alt={zoomedImage.title} className="photo-zoom-modal-img" />
          </div>
        </div>
      )}
    </div>
  );
}
