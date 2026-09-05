import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navigation } from 'lucide-react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { SkillCategoryGrid, SKILL_CATEGORIES } from '../components/SkillCategoryGrid';
import { PricingBreakdownCard } from '../components/PricingBreakdownCard';
import { GenderPreferenceSelector } from '../components/GenderPreferenceSelector';
import { useCreateBooking } from '../hooks/useBooking';
import { usePricePreview } from '../hooks/usePricePreview';
import { useLanguage } from '../hooks/useLanguage';
import { LanguageToggle } from '../components/LanguageToggle';
import './Book.css';

// Fix for default Leaflet icon not showing correctly in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function LocationPicker({
  position,
  setPosition,
}: {
  position: [number, number];
  setPosition: (pos: [number, number]) => void;
}) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng]);
    },
  });
  return position ? <Marker position={position} /> : null;
}

export function Book() {
  const [step, setStep] = useState(1);
  const [skill, setSkill] = useState<string | null>(null);
  const [position, setPosition] = useState<[number, number]>([26.9124, 75.7873]); // Default Jaipur
  const [urgency, setUrgency] = useState<'normal' | 'urgent' | 'emergency'>('normal');
  const [genderPreference, setGenderPreference] = useState<'any' | 'female' | 'male'>('any');
  const [description, setDescription] = useState('');
  const [urgency, setUrgency] = useState<'normal' | 'urgent' | 'emergency'>('normal');

  const navigate = useNavigate();
  const createBooking = useCreateBooking();
  const pricePreview = usePricePreview(skill, position[0], position[1], urgency);
  const { t } = useLanguage();

  const handleNext = () => setStep((s) => Math.min(s + 1, 4));
  const handleBack = () => setStep((s) => Math.max(s - 1, 1));

  const handleUseMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setPosition([pos.coords.latitude, pos.coords.longitude]),
        (_err) => alert('Could not get location. Please click on the map.'),
      );
    }
  };

  const handleSubmit = async () => {
    if (!skill) return;
    try {
      const result = await createBooking.mutateAsync({
        skill,
        lat: position[0],
        lng: position[1],
        urgency,
        gender_preference: genderPreference,
        description: description || undefined,
        urgency,
      });
      navigate(`/booking/${result.booking_id}`);
    } catch (error) {
      console.error('Failed to create booking', error);
      alert('Failed to submit booking. Please try again.');
    }
  };

  const getSkillLabel = (id: string) => SKILL_CATEGORIES.find((s) => s.id === id)?.label || id;

  return (
    <div className="book-container">
      <div className="wizard-header">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 'var(--spacing-md)',
          }}
        >
          <h1 className="wizard-title" style={{ margin: 0 }}>
            {t('nav.book')}
          </h1>
          <LanguageToggle />
        </div>
        <p className="wizard-subtitle">Find a cooperative worker near you.</p>
      </div>

      <div className="wizard-progress">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`progress-step ${step === i ? 'active' : ''} ${step > i ? 'completed' : ''}`}
          >
            {i}
          </div>
        ))}
      </div>

      <div className="wizard-step-content">
        {step === 1 && (
          <div>
            <h2 className="step-title">What do you need help with?</h2>
            <SkillCategoryGrid
              selectedSkill={skill}
              onSelect={(s) => {
                setSkill(s);
                setTimeout(handleNext, 300); // Auto-advance
              }}
            />
            <div className="wizard-actions" style={{ justifyContent: 'flex-end' }}>
              <button className="btn-primary" disabled={!skill} onClick={handleNext}>
                Continue
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="step-title">Where do you need the worker?</h2>
            <button className="btn-secondary location-btn" onClick={handleUseMyLocation}>
              <Navigation size={18} /> Use My Location
            </button>
            <div className="map-container">
              <MapContainer center={position} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <LocationPicker position={position} setPosition={setPosition} />
              </MapContainer>
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
              Click on the map to place the pin. (Lat: {position[0].toFixed(4)}, Lng:{' '}
              {position[1].toFixed(4)})
            </p>

            <div className="wizard-actions">
              <button className="btn-secondary" onClick={handleBack}>
                Back
              </button>
              <button className="btn-primary" onClick={handleNext}>
                Continue to Price Preview
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="step-title">Transparent Pricing Preview</h2>
            <PricingBreakdownCard
              skillLabel={skill ? getSkillLabel(skill) : ''}
              locationText={`${position[0].toFixed(4)}, ${position[1].toFixed(4)}`}
              urgency={urgency}
              onUrgencyChange={setUrgency}
              pricingData={pricePreview.data}
              isLoading={pricePreview.isLoading}
              error={pricePreview.error ? (pricePreview.error as Error).message : null}
            />

            <div className="wizard-actions">
              <button className="btn-secondary" onClick={handleBack}>
                Back
              </button>
              <button
                className="btn-primary"
                onClick={handleNext}
                disabled={pricePreview.isLoading || !!pricePreview.error}
              >
                Confirm Price & Continue
              </button>
            </div>
          </div>
        )}

        {step === 4 && (
          <div>
            <h2 className="step-title">Review & Preferences</h2>
            <div style={{ marginBottom: '24px' }}>
              <div className="summary-item">
                <span className="summary-label">Service</span>
                <span className="summary-value">{skill ? getSkillLabel(skill) : ''}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Location</span>
                <span className="summary-value">
                  {position[0].toFixed(4)}, {position[1].toFixed(4)}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Estimated Fixed Price</span>
                <span className="summary-value">
                  {pricePreview.data
                    ? `₹${Number(pricePreview.data.final_price).toFixed(2)}`
                    : 'Calculated'}
                </span>
              </div>
            </div>

            <GenderPreferenceSelector selected={genderPreference} onChange={setGenderPreference} />

            <div style={{ marginBottom: '24px' }}>
              <label className="summary-label" style={{ display: 'block', marginBottom: '8px' }}>
                Booking Urgency
              </label>
              <div className="urgency-chips">
                <button
                  type="button"
                  className={`urgency-chip ${urgency === 'normal' ? 'selected' : ''}`}
                  onClick={() => setUrgency('normal')}
                >
                  🕐 Standard
                </button>
                <button
                  type="button"
                  className={`urgency-chip ${urgency === 'urgent' ? 'selected' : ''}`}
                  onClick={() => setUrgency('urgent')}
                >
                  ⚡ Urgent (+20%)
                </button>
                <button
                  type="button"
                  className={`urgency-chip ${urgency === 'emergency' ? 'selected' : ''}`}
                  onClick={() => setUrgency('emergency')}
                >
                  🚨 Emergency (+35%)
                </button>
              </div>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label className="summary-label" style={{ display: 'block', marginBottom: '8px' }}>
                Job Description (Optional)
              </label>
              <textarea
                className="input-field"
                rows={3}
                placeholder="E.g. The kitchen sink is leaking..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="wizard-actions">
              <button className="btn-secondary" onClick={handleBack}>
                Back
              </button>
              <button
                className="btn-primary"
                onClick={handleSubmit}
                disabled={createBooking.isPending}
              >
                {createBooking.isPending ? 'Submitting...' : 'Find a Worker'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
