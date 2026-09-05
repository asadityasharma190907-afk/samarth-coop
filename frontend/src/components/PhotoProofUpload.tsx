import React, { useState, useRef } from 'react';
import { Camera, CheckCircle2, UploadCloud, AlertCircle, Loader2 } from 'lucide-react';
import './PhotoProofUpload.css';

export interface PhotoProofUploadProps {
  bookingId: string;
  photoType: 'before' | 'after';
  currentPhotoUrl?: string | null;
  onUploaded?: (url: string) => void;
  disabled?: boolean;
}

export function PhotoProofUpload({
  bookingId,
  photoType,
  currentPhotoUrl,
  onUploaded,
  disabled = false,
}: PhotoProofUploadProps) {
  const [photoUrl, setPhotoUrl] = useState<string | null>(currentPhotoUrl || null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const title = photoType === 'before' ? 'Before Work Photo' : 'After Work Photo';
  const subtitle =
    photoType === 'before'
      ? 'Take a photo of the site before starting work'
      : 'Take a photo showing the finished work';

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate client-side size (< 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage('File size must be less than 5MB');
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const endpoint = `/bookings/${bookingId}/photos/${photoType}`;
      const token = localStorage.getItem('samarth_token');
      const baseURL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

      const response = await fetch(`${baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to upload photo');
      }

      const data = await response.json();
      const uploadedUrl = data.photo_url || data[`${photoType}_photo_url`];
      setPhotoUrl(uploadedUrl);
      if (onUploaded) {
        onUploaded(uploadedUrl);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error uploading photo');
    } finally {
      setIsUploading(false);
    }
  };

  const getFullImageUrl = (url: string) => {
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    const baseURL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
    return `${baseURL}${url}`;
  };

  return (
    <div className="photo-proof-upload" data-testid={`photo-upload-${photoType}`}>
      <div className="photo-upload-header">
        <div className="photo-upload-title-group">
          <span className="photo-upload-title">{title}</span>
          <span className="photo-upload-subtitle">{subtitle}</span>
        </div>
        {photoUrl && (
          <span className="photo-uploaded-badge">
            <CheckCircle2 size={14} /> Uploaded
          </span>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileChange}
        style={{ display: 'none' }}
        disabled={disabled || isUploading}
        data-testid={`file-input-${photoType}`}
      />

      {photoUrl ? (
        <div className="photo-preview-container">
          <img
            src={getFullImageUrl(photoUrl)}
            alt={`${title} preview`}
            className="photo-preview-img"
          />
          <button
            type="button"
            className="photo-replace-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || isUploading}
          >
            <Camera size={16} /> Retake Photo
          </button>
        </div>
      ) : (
        <button
          type="button"
          className={`photo-dropzone-btn ${isUploading ? 'uploading' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || isUploading}
        >
          {isUploading ? (
            <div className="photo-upload-spinner">
              <Loader2 size={24} className="spin-icon" />
              <span>Uploading photo...</span>
            </div>
          ) : (
            <div className="photo-dropzone-content">
              <div className="photo-dropzone-icon">
                <UploadCloud size={24} />
              </div>
              <span className="photo-dropzone-cta">Upload or Capture Photo</span>
              <span className="photo-dropzone-hint">JPEG, PNG or WebP up to 5MB</span>
            </div>
          )}
        </button>
      )}

      {errorMessage && (
        <div className="photo-upload-error">
          <AlertCircle size={14} />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
