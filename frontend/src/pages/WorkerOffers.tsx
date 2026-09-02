import React from 'react';
import { Radio } from 'lucide-react';
import { useWorkerOffers } from '../hooks/useOffers';
import { OfferCard } from '../components/OfferCard';
import './WorkerOffers.css';

export function WorkerOffers() {
  const { data: offers, isLoading, isError } = useWorkerOffers();

  if (isLoading) {
    return (
      <div className="worker-offers-container">
        <div className="worker-offers-header">
          <h1 className="worker-offers-title">Job Offers</h1>
          <p className="worker-offers-subtitle">Loading your inbox...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="worker-offers-container">
        <div className="worker-offers-header">
          <h1 className="worker-offers-title">Job Offers</h1>
          <p className="worker-offers-subtitle text-status-error">
            Failed to load offers. Please try again.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="worker-offers-container">
      <div className="worker-offers-header">
        <h1 className="worker-offers-title">Job Offers</h1>
        <p className="worker-offers-subtitle">
          {offers && offers.length > 0
            ? `You have ${offers.length} active offer${offers.length > 1 ? 's' : ''}.`
            : 'Listening for nearby jobs...'}
        </p>
      </div>

      {!offers || offers.length === 0 ? (
        <div className="empty-state animate-fade-in">
          <Radio size={48} className="radar-icon" />
          <h3>No offers right now</h3>
          <p>When a citizen requests a service near you, it will appear here automatically.</p>
        </div>
      ) : (
        <div className="offers-list">
          {offers.map((offer) => (
            <OfferCard key={offer.id} offer={offer} />
          ))}
        </div>
      )}
    </div>
  );
}
